FROM python:3.7-alpine

MAINTAINER faq@cryptic-game.net

ENV MYSQL_PORT 3306

WORKDIR /app

RUN pip install pipenv

ADD ./Pipfile /app/
ADD ./Pipfile.lock /app/

RUN pipenv sync

ADD . /app/

RUN pipenv run test

CMD pipenv run prod
