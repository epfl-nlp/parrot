#!/bin/bash

echo "Starting the application..."
gunicorn \
    -w ${GUNICORN_NUM_WORKERS:-4} \
    --threads ${GUNICORN_NUM_THREADS:-4} \
    -b 0.0.0.0:${FLASK_RUN_PORT} \
    --timeout ${GUNICORN_TIMEOUT:-180} \
    --capture-output \
    --access-logfile=- \
    --log-file=- \
    "server:init_app()"