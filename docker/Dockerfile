FROM alpine:3.9

ADD . /opt/cloud
WORKDIR /opt/cloud
USER root
#RUN ls -al /opt/cloud
RUN apk update && apk add --no-cache python3 bash && pip3 install --no-cache --upgrade -r /opt/cloud/requirements.txt && rm -rf /var/lib/apt/lists/*

RUN sed -i -e 's/\r$//' /opt/cloud/script/bootstrap.sh
ENV DJANGO_HOST=0.0.0.0 \
	DJANGO_PORT=8000 \
	DJANGO_ALLOWED_HOSTS=127.0.0.1 \
	RQ_REDIS_HOST=127.0.0.1 \
	RQ_REDIS_PORT=6379 \
	RQ_REDIS_DB=0 \
	WITH_REDIS=1

CMD ["bash", "/opt/cloud/script/bootstrap.sh"]

