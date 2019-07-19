FROM python:3.7-alpine

MAINTAINER faq@cryptic-game.net

ENV MYSQL_PORT 3306

WORKDIR /app

ADD ./Pipfile /app/

RUN pip install pipenv
RUN pipenv install

ADD . /app/

CMD pipenv run prod
