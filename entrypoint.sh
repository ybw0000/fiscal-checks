#!/bin/bash

if [ "$DEBUG" = "true" ]; then
  uvicorn --reload --host 0.0.0.0 --port 8000 src.main:app
else
  gunicorn -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py src.main:app
fi
