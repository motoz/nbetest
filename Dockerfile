FROM ubuntu:18.04
MAINTAINER e1z0

RUN apt-get update && apt-get install -y software-properties-common language-pack-en-base python3 python3-pip nano python3-simplejson && \
    export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8 && pip3 install pycrypto paho-mqtt && \
    rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apk/*

COPY . /app

ENTRYPOINT ["/app/docker_init"]
 
