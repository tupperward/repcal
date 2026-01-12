FROM python:3.10-alpine

WORKDIR /app

# Copy only needed shared files (ordinal function)
COPY repcal_shared/__init__.py /app/repcal_shared/__init__.py
COPY repcal_shared/utils.py /app/repcal_shared/utils.py

# Copy webhook script
COPY webhook/webhook.py .

# Install dependencies
RUN pip install discord requests flask

CMD ["python", "webhook.py"]
