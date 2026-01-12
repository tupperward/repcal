FROM python:3.10-alpine

WORKDIR /app

# Copy shared package from parent directory
COPY repcal_shared/ /app/repcal_shared/

# Install shared dependencies
RUN pip install -r repcal_shared/requirements.txt

# Copy bot-specific files
COPY bot/bot.py .

# Install bot-specific dependencies (requests added for image fetching)
RUN pip install pytz atproto requests

ENV TZ='Europe/Paris'

CMD ["python", "bot.py"]
