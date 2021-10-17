FROM python:3.10

RUN apt-get update && apt-get install -y cron && cron

RUN mkdir /etc/repcal

WORKDIR /etc/repcal

COPY . /etc/repcal/

RUN chmod 0744 /etc/repcal

RUN cron /etc/crontab

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["python3", "app.py", "&"]

