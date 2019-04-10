#!/bin/bash -e
# by Evgeniy Bondarenko <Bondarenko.Hub@gmail.com>
# last changes 01.03.2019 Updated


dockerhub=${dockerhub:-"docker.u2035s.ru"}
name=${name:-"unti/functional-checks"}
tag=${tag:-"stage"}
version="_$(date +%Y-%m-%d_%H-%M-%S)"
NO_CACHE=${NO_CACHE:-"random"}

docker build --build-arg NO_CACHE=${NO_CACHE}  -t ${dockerhub}/${name}:latest -t ${dockerhub}/${name}:${tag} -t ${dockerhub}/${name}:${tag}${version}  .

if [ ${tag} == 'prod' ]; then
docker push ${dockerhub}/${name}:${tag}${version} && docker push ${dockerhub}/${name}:${tag}
else
docker push ${dockerhub}/${name}:${tag} && docker push ${dockerhub}/${name}:latest
fi
