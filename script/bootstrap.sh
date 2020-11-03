#!sh

#echo "rm old migrations..."
#rm -rf /opt/cloud/mysite/tester/migrations/*
#echo "make migrations..."
#python3 /opt/cloud/mysite/manage.py makemigrations
echo "migrate..."
python3 /opt/cloud/mysite/manage.py migrate
echo "loaddata job..."
python3 /opt/cloud/mysite/manage.py loaddata /opt/cloud/mysite/tester/fixtures/initial_job.yaml
echo "loaddata scheduler..."
python3 /opt/cloud/mysite/manage.py loaddata /opt/cloud/mysite/tester/fixtures/initial_scheduler.yaml
echo "nohup rqworker..."
nohup python3 /opt/cloud/mysite/manage.py rqworker default > /opt/cloud/rqworker.log 2>&1 &
echo "nohup rqscheduler..."
nohup rqscheduler --host $RQ_REDIS_HOST --port $RQ_REDIS_PORT --db $RQ_REDIS_DB > /opt/cloud/rqscheduler.log 2>&1 &
echo "runserver..."
python3 /opt/cloud/mysite/manage.py runserver $DJANGO_HOST:$DJANGO_PORT

