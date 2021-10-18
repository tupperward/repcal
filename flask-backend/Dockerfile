FROM python:3.10

RUN mkdir /etc/repcal

WORKDIR /etc/repcal

COPY . /etc/repcal/

RUN chmod 0744 /etc/repcal

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["python3", "app.py", "&"]

