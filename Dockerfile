FROM python:3.10-slim-bullseye

RUN mkdir /repcal

WORKDIR /repcal

COPY . /repcal

RUN chown daemon /repcal
RUN chmod 705 /repcal
RUN pip install -r requirements.txt

ENV TZ="Europe/Paris"

EXPOSE 8000
USER daemon
CMD ["sh", "./startup.sh"]