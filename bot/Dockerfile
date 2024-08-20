FROM python:3.10-alpine

COPY calendar.db .
COPY images /images
COPY bot.py .

RUN pip install sqlalchemy unidecode repcal pytz bsky-bridge Pillow

CMD ["python", "bot.py"]