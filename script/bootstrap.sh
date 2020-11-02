#!bash

#if [ $WITH_REDIS -eq 1 ]

/opt/cloud/mysite/manage.py migrate
nohup /opt/cloud/mysite/manage.py rqworker default > /opt/cloud/rqworker.log 2>&1 &
/opt/cloud/mysite/manage.py runserver $DJANGO_HOST:$DJANGO_PORT

