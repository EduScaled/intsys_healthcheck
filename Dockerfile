FROM python:3.7-stretch

LABEL maintainer="Evgeniy Bondarenko <Bondarenko.Hub@gmail.com>"
MAINTAINER EvgeniyBondarenko "Bondarenko.Hub@gmail.com"

EXPOSE 80
WORKDIR /opt
ENTRYPOINT ["./docker-entrypoint.sh" ]

CMD gunicorn "app:init_func()" -b 0.0.0.0:80 -k aiohttp.GunicornWebWorker

RUN apt-get update \
    && apt-get install -y python-dev python-pip dnsutils telnet curl vim \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip3 install pipenv

COPY Pipfile ./

RUN  pipenv install --skip-lock --system --deploy

COPY . ./