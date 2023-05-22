FROM python:3.10-alpine

COPY webhook.py .

RUN pip install discord requests flask

CMD ["python", "webhook.py"]