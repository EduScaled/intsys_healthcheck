#!/bin/bash
# by Evgeniy Bondarenko <Bondarenko.Hub@gmail.com>
# last changes 06.01.2018 Create

dockerhub='docker.u2035s.ru/'
name=intsys-healthcheck
tag=latest

docker build -t ${dockerhub}${name}:${tag} -t ${dockerhub}${name}:${tag}${version}  . && \
docker push ${dockerhub}${name}:${tag}${version} && docker push ${dockerhub}${name}:${tag}