FROM python:3.10-alpine

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
COPY modules/webhook.py .

ENV TZ="Europe/Paris"

CMD ["python", "webhook.py"]