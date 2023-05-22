FROM faucet/python3

COPY webhook.py .

RUN pip install discord requests flask

CMD ["python", "webhook.py"]