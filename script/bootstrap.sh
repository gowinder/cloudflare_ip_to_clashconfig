#!sh

python3 /opt/cloud/mysite/manage.py migrate
python3 /opt/cloud/mysite/manage.py loaddata /opt/cloud/mysite/tester/fixtures/initial_data.yaml
nohup python3 /opt/cloud/mysite/manage.py rqworker default > /opt/cloud/rqworker.log 2>&1 &
python3 /opt/cloud/mysite/manage.py runserver $DJANGO_HOST:$DJANGO_PORT

