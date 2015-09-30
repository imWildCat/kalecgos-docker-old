FROM python:2.7

MAINTAINER Michael Chong <wildcat.name@gmail.com>

WORKDIR /app/kalecgos

ADD ./kalecgos/requirements.txt /app/kalecgos/requirements.txt

RUN pip install -r requirements.txt

EXPOSE 5000

ENV ENV production

ADD . /app

CMD python kalecgos/web_server.py