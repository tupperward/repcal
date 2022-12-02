FROM python:3.10-slim-bullseye

RUN mkdir /etc/repcal

WORKDIR /etc/repcal

COPY . /etc/repcal/

RUN chown daemon /etc/repcal
RUN chmod 705 /etc/repcal
RUN pip install -r requirements.txt

EXPOSE 8000
USER daemon
CMD ["sh", "./startup.sh"]