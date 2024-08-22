FROM python:3.10-alpine

COPY calendar.db .
COPY images /images
COPY bot.py .

ENV  TZ='Europe/Paris'

RUN pip install sqlalchemy unidecode repcal pytz atproto

CMD ["python", "bot.py"]