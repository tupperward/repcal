FROM python:3.13-alpine

RUN mkdir /repcal

WORKDIR /repcal

# Copy shared package first
COPY repcal_shared/ /repcal/repcal_shared/

# Install shared dependencies
RUN pip install -r repcal_shared/requirements.txt

# Copy webhook module (needed for success page)
COPY webhook/ /repcal/webhook/

# Copy application code
COPY web/app.py web/startup.sh web/requirements.txt ./
COPY web/static/ ./static/
COPY web/templates/ ./templates/

# Install app-specific dependencies
RUN pip install -r requirements.txt

RUN chown -R daemon /repcal
RUN chmod 705 /repcal

ENV TZ="Europe/Paris"

EXPOSE 8000
USER daemon
ENTRYPOINT [ "sh","./startup.sh" ]