import logging
import os
import random
import sys
import time
from datetime import datetime, timezone

import couchdb
import requests
from bs4 import BeautifulSoup

from . import api

log = logging.getLogger("women_index")

DB_NAME = "fwf_women_index"
TEAM_CACHE_ID = "team_country"
META_ID = "meta"
PHASES = 4
RETRY_WAITS = (30, 60, 120)  # seconds. CHPP outages are usually short
MAX_FAILURE_RATE = 0.02  # more than 2 % failed requests: abort, keep last week's index


class CrawlAborted(RuntimeError):
    """Too many failures: don't write a half-empty index."""


def _db():
    server = couchdb.Server(os.environ["COUCHDB_CONNECTION_STRING"])
    return server[DB_NAME] if DB_NAME in server else server.create(DB_NAME)


def _fmt(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m{s:02d}s" if h else f"{m}m{s:02d}s"


def _phase(n, title, **info):
    extra = ", ".join(f"{k}={v}" for k, v in info.items())
    log.info("▶ phase %d/%d: %s%s", n, PHASES, title, f" ({extra})" if extra else "")
    return time.monotonic()


def _done(n, started, **info):
    extra = ", ".join(f"{k}={v}" for k, v in info.items())
    log.info("✔ phase %d/%d done in %s%s", n, PHASES, _fmt(time.monotonic() - started),
             f": {extra}" if extra else "")


def _progress(label, i, total, started, every):
    if i % every == 0 or i == total:
        elapsed = time.monotonic() - started
        eta = elapsed / i * (total - i)
        log.info("  %s %d/%d (%d%%), elapsed %s, eta %s",
                 label, i, total, 100 * i // total, _fmt(elapsed), _fmt(eta))


def _get(name, token, delay, **params):
    """One CHPP request with retries on network errors, then a polite pause."""
    for attempt, wait in enumerate((*RETRY_WAITS, None), 1):
        try:
            xml = api.ht_get_data(name, fernet_token=token, **params)
            time.sleep(delay)
            return xml
        except requests.exceptions.RequestException as e:
            if wait is None:
                raise
            log.warning("  %s %s: %s, retry %d/%d in %ds",
                        name, params, type(e).__name__, attempt, len(RETRY_WAITS), wait)
            time.sleep(wait)


def _check_failures(what, failed, total):
    if total and len(failed) / total > MAX_FAILURE_RATE:
        raise CrawlAborted(f"{len(failed)}/{total} {what} failed (> {MAX_FAILURE_RATE:.0%})")
    if failed:
        log.warning("  %d %s failed, within tolerance: %s", len(failed), what, failed[:10])


def human_teams(leaguedetails_xml):
    """Team ids of a series, without bots (UserId 0)."""
    soup = BeautifulSoup(leaguedetails_xml, "xml")
    return [
        t.TeamID.text
        for t in soup.find_all("Team")
        if t.UserId is not None and t.UserId.text.strip() != "0"
    ]


def candidates(flag_id, exclude=()):
    """Women's teams for this flag from the last crawl, shuffled for load balancing."""
    doc = _db().get(f"flag_{flag_id}") or {}
    teams = [t for t in doc.get("teams", []) if t not in exclude]
    random.shuffle(teams)
    return teams


def build(token, delay=1.0, max_units=None):
    t0 = time.monotonic()
    db = _db()
    cache_doc = db.get(TEAM_CACHE_ID) or {"_id": TEAM_CACHE_ID, "teams": {}}
    cache = cache_doc["teams"]

    # 1. the women's league tree
    p = _phase(1, "league tree", league=api.WOMEN_LEAGUE_ID, delay=f"{delay}s")
    levels = api.ht_get_leaguelevels(
        _get("leaguelevels", token, delay, LeagueID=api.WOMEN_LEAGUE_ID)
    )
    units = [u.strip() for lvl in levels["league_levels"] for u in lvl["lluid_list"]]
    units = [u for u in units if u]
    if max_units:
        units = units[:max_units]
    _done(1, p, levels=levels["league_depth"], series=len(units),
          dry_run=bool(max_units))

    # 2. human teams per series
    p = _phase(2, "series → human teams", series=len(units))
    humans, failed = [], []
    for i, unit in enumerate(units, 1):
        try:
            humans += human_teams(_get("teams_in_series", token, delay, leagueLevelUnitID=unit))
        except Exception:
            log.exception("  series %s failed", unit)
            failed.append(unit)
        _progress("series", i, len(units), p, every=100)
    humans = list(dict.fromkeys(humans))
    _check_failures("series", failed, len(units))
    _done(2, p, human_teams=len(humans))

    # 3. CountryID for new teams only
    new = [t for t in humans if t not in cache]
    p = _phase(3, "team → country", new=len(new), cached=len(humans) - len(new))
    failed = []
    for i, team_id in enumerate(new, 1):
        try:
            xml = _get("teamdetails", token, delay, teamID=team_id, includeFlags="false")
            cache[team_id] = api.ht_get_team(xml)[team_id]["team_real_country_id"]
        except Exception:
            log.exception("  team %s failed", team_id)
            failed.append(team_id)
        if i % 200 == 0:
            db.save(cache_doc)
            log.info("  checkpoint saved (%d teams cached)", len(cache))
        _progress("teamdetails", i, len(new), p, every=100)
    db.save(cache_doc)  # the cache is always worth keeping, even if we abort below
    _check_failures("teams", failed, len(new))
    _done(3, p, cached_total=len(cache))

    # 4. write the index (only reached if phases 2 and 3 were healthy)
    p = _phase(4, "write index")
    flag_map = api.get_country_flag_map(token)
    by_flag, unmapped = {}, 0
    for team_id in humans:
        flag = flag_map.get(cache.get(team_id, ""))
        if flag:
            by_flag.setdefault(flag, []).append(team_id)
        else:
            unmapped += 1
    if unmapped:
        log.warning("  %d teams without a flag (unknown CountryID)", unmapped)

    now = datetime.now(timezone.utc).isoformat()
    for flag, teams in by_flag.items():
        doc = db.get(f"flag_{flag}") or {"_id": f"flag_{flag}"}
        doc.update(teams=teams, updated=now)
        db.save(doc)
    for row in db.view("_all_docs"):
        if row.id.startswith("flag_") and row.id[len("flag_"):] not in by_flag:
            doc = db[row.id]
            doc.update(teams=[], updated=now)
            db.save(doc)

    meta = db.get(META_ID) or {"_id": META_ID}
    meta.update(updated=now, series=len(units), teams=len(humans), flags=len(by_flag),
                duration=_fmt(time.monotonic() - t0), dry_run=bool(max_units))
    db.save(meta)
    _done(4, p, flags=len(by_flag), teams=sum(map(len, by_flag.values())))
    log.info("🏁 crawl finished in %s", _fmt(time.monotonic() - t0))


def index_ready():
    """True once at least one complete crawl has written the index."""
    return _db().get(META_ID) is not None


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    max_units = os.environ.get("CRAWL_MAX_UNITS")
    try:
        build(
            os.environ["CRAWLER_FERNET_TOKEN"],
            delay=float(os.environ.get("CRAWL_DELAY", "1.0")),
            max_units=int(max_units) if max_units else None,
        )
    except CrawlAborted as e:
        log.error("✖ crawl aborted, last week's index is kept: %s", e)
        sys.exit(1)
