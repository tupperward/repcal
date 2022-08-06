FROM python:3.10-alpine

RUN mkdir /etc/repcal

WORKDIR /etc/repcal

COPY ./app.py /etc/repcal/
COPY ./requirements.txt /etc/repcal/
COPY ./static/ /etc/repcal/

RUN chmod 0744 /etc/repcal

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["python3", "app.py", "&"]

