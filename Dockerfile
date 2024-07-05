FROM python:3.11-bookworm

RUN mkdir /app
RUN mkdir /app/static
RUN mkdir /app/templates
RUN mkdir /app/audio

COPY static/ /app/static
COPY templates/ /app/templates
COPY entities.py /app
COPY functions.py /app
COPY main.py /app
COPY openai_functions.py /app
COPY requirements.txt /app

ENV CACHE_TTL=10
ENV HOST=0.0.0.0
ENV PORT=8000

RUN cd /app && pip install -r requirements.txt

WORKDIR /app

EXPOSE 8000

CMD [ "/usr/local/bin/gunicorn", "-w", "4", "main:app" ]
