#!/bin/sh

python manage.py collectstatic --noinput
gunicorn --reload -b 0.0.0.0:8000 areus.wsgi:application
