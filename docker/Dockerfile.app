# syntax=docker/dockerfile:1

# build with: "docker build -t "fun-with-flags-app:latest" -f Dockerfile.app --build-arg ck=GK
#																			 --build-arg cs=CS
#																			 --bulid-arg fls=FLS
#																			 --bulid-arg fes=FES
#																			 --build-arg cdbcs=CDBCS ."



FROM python:3.12.1-bookworm


ARG ck
ARG cs
ARG fls
ARG fes
ARG cdbcs

ENV HATTRICK_OAUTH_CONSUMER_KEY $ck
ENV HATTRICK_OAUTH_CONSUMER_SECRET $cs
ENV FLASK_SECRET $fls
ENV FERNET_SECRET $fes
ENV COUCHDB_CONNECTION_STRING $cdbcs


WORKDIR .

EXPOSE 8000

RUN pip3 install hattrick-fwf

CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "4", "-t", "120", "fun_with_flags:create_app()"]
