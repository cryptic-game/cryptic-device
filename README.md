cryptic-device [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=cryptic-game_cryptic-device&metric=coverage)](https://sonarcloud.io/dashboard?id=cryptic-game_cryptic-device)
============

The official device microservice of Cryptic (https://cryptic-game.net/).

## Testing with Docker

If you want to test this microservice you can simply build and run a 
container with docker-compose:

`docker-compose up -d`

The microservice is available on port `1241`.

## Testing with pipenv

You can also test it without docker using pipenv:

`pipenv run dev` or `pipenv run prod`

To install the dependencies manually use:

`pipenv install`

If you only need a mysql-server you can bring it up with:

`docker-compose up -d db`

## Docker-Hub

This microservice is online on docker-hub (https://hub.docker.com/r/useto/cryptic-device/).

## API
[API Documentation](https://github.com/cryptic-game/cryptic-device/wiki)
