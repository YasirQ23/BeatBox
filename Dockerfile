FROM python:slim

RUN useradd beatbox

WORKDIR /home/Beatbox

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY Beatbox.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP Beatbox.py

RUN chown -R Beatbox:Beatbox ./
USER Beatbox

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]