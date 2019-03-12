FROM python:3.7-stretch
LABEL maintainer="Nick Lubyanov <lubyanov@gmail.com>"
MAINTAINER NickLubyanov "lubyanovb@gmail.com"

EXPOSE 80
WORKDIR /opt

CMD gunicorn "app:init_func()" -b 0.0.0.0:80 -k aiohttp.GunicornWebWorker

COPY . ./

RUN apt-get update \
    && apt-get install -y python-dev python-pip dnsutils telnet curl vim \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip3 install pipenv \
    && pipenv install --skip-lock --system --deploy