#!/bin/sh
exec gunicorn -b :3000 --access-logfile - --error-logfile - frontend:app
