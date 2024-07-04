# syntax=docker/dockerfile:1.7-labs

FROM python:3.11-bookworm

RUN mkdir /app

COPY --exclude=venv --exclude=*.pyc --exclude=*.pyo --exclude=.env* --exclude=.git* * /app

RUN cd /app && pip install -r requirements.txt

WORKDIR /app

EXPOSE 8000

CMD [ "/usr/local/bin/gunicorn", "-w", "4", "main:app" ]
