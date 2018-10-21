cryptic-device
============

The offical device microservice of Cryptic (https://cryptic-game.net/)

## Testing with Docker

If you want to test this microservice you can simply build and run a container with docker-compose:

`docker-compose up`

The microservice is available on port `1241`.

## Testing with pipenv

You can also test it without docker using pipenv:

`pipenv run dev` or `pipenv run prod`

To install the dependencies manually use:

`pipenv install`

## Docker-Hub

This microservice is online on docker-hub (https://hub.docker.com/r/useto/cryptic-device/).
