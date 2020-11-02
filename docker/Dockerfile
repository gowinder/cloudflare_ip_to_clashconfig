FROM alpine:3.9

ADD . /opt/cloud
WORKDIR /opt/cloud
USER root
RUN apk update && apk add -y --no-cache python3 && pip3 install --no-cache --upgrade -r /opt/cloud/requirements.txt && rm -rf /var/lib/apt/lists/*

ENV DJANGO_HOST=0.0.0.0
ENV DJANGO_PORT=8000
ENV DJANGO_ALLOWED_HOSTS=127.0.0.1
ENV RQ_REDIS_HOST=127.0.0.1
ENV WITH_REDIS=1

ENTRYPOINT ["/opt/cloud/script/bootstrap.sh"]

