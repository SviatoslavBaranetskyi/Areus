#!/bin/sh

python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn --reload -b 0.0.0.0:8000 areus.wsgi:application
