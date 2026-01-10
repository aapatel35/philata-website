#!/bin/bash
PORT="${PORT:-8080}"
echo "Starting server on port $PORT"
exec gunicorn --bind "0.0.0.0:$PORT" --workers 4 --timeout 120 app:app
