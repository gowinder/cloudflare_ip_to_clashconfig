#!sh

python3 /opt/cloud/mysite/manage.py migrate
python3 /opt/cloud/mysite/manage.py loaddata /opt/cloud/mysite/tester/fixtures/initial_job.yaml
python3 /opt/cloud/mysite/manage.py loaddata /opt/cloud/mysite/tester/fixtures/initial_scheduler.yaml
nohup python3 /opt/cloud/mysite/manage.py rqworker default > /opt/cloud/rqworker.log 2>&1 &
nohup rqscheduler --host $RQ_REDIS_HOST --port $RQ_REDIS_PORT --db $RQ_REDIS_DB > /opt/cloud/rqscheduler.log 2>&1 &
python3 /opt/cloud/mysite/manage.py runserver $DJANGO_HOST:$DJANGO_PORT

