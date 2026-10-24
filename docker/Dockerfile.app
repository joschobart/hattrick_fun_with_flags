# syntax=docker/dockerfile:1

# build with: "docker build -t "fun-with-flags-app:latest" -f Dockerfile.app --build-arg ck=GK
#																			 --build-arg cs=CS
#																			 --bulid-arg fls=FLS
#																			 --bulid-arg fes=FES
#																			 --build-arg cdbcs=CDBCS 
#                                                                            --build-arg stwhst=STWHST
#                                                                            --build-arg stwhs=STWHS
#                                                                            --build-arg stest=STEST
#                                                                            --build-arg stes=STES
#                                                                            --build-arg stpit=STPIT
#                                                                            --build-arg stpi=STPI ."


FROM python:3.12-bookworm


ARG ck
ARG cs
ARG fls
ARG fes
ARG cdbcs
ARG stwhst
ARG stwhs
ARG stest
ARG stes
ARG stpit
ARG stpi

ENV TZ=CET
ENV HATTRICK_OAUTH_CONSUMER_KEY=$ck
ENV HATTRICK_OAUTH_CONSUMER_SECRET=$cs
ENV FLASK_SECRET=$fls
ENV FERNET_SECRET=$fes
ENV COUCHDB_CONNECTION_STRING=$cdbcs
ENV STRIPE_WEBHOOK_SECRET_TEST=$stwhst
ENV STRIPE_WEBHOOK_SECRET=$stwhs
ENV STRIPE_ENDPOINT_SECRET_TEST=$stest
ENV STRIPE_ENDPOINT_SECRET=$stes
ENV STRIPE_PRICE_ITEM_TEST=$stpit
ENV STRIPE_PRICE_ITEM=$stpi


COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /uvx /bin/

# Use the image's own Python. Never download one into /root (random UID can't read it)
ENV UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=/usr/local/bin/python3.12

ENV HOME=/tmp
ENV PYTHONUNBUFFERED=1

COPY . /app
WORKDIR /app


RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/CET /etc/localtime


# Use uv to install dependencies
RUN uv sync --frozen --no-dev
RUN chmod -R +x .venv/bin
ENV PATH="/app/.venv/bin:$PATH"


RUN pybabel extract -F babel.cfg -o messages.pot . && \
    pybabel update -i messages.pot -d fun_with_flags/translations/ && \
    pybabel compile -d fun_with_flags/translations


RUN chgrp -R 0 /app && chmod -R g=u /app


EXPOSE 8000


CMD ["gunicorn", "-b", "0.0.0.0:8000", \
                "--threads", "4", \
                "-t", "120", \
                "--log-level", "info", \
                "--access-logfile", "-", \
                "--error-logfile", "-", \
                "fun_with_flags:create_app()"]
