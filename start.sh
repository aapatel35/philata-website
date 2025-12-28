#!/bin/sh
exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 4 app:app
