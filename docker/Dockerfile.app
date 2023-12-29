# syntax=docker/dockerfile:1

FROM python:3.12.1-bookworm

WORKDIR .

EXPOSE 8000

RUN pip3 install hattrick-fwf

CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "4", "-t", "120", "fun_with_flags:create_app()"]
