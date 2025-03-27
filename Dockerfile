FROM python:3.10-slim-bullseye

RUN mkdir /repcal

WORKDIR /repcal

COPY . /repcal

RUN chown daemon /repcal
RUN chmod 705 /repcal
RUN chown daemon /repcal/startup.sh
RUN chmod 705 /repcal/startup.sh
RUN pip install -r requirements.txt

ENV TZ="Europe/Paris"

EXPOSE 8000
USER daemon
ENTRYPOINT [ "sh","./startup.sh" ]