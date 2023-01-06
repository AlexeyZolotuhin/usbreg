#!/bin/sh
flask db upgrade
exec gunicorn -b :4000 --access-logfile - --error-logfile - backend:app
