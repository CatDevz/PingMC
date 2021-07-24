#!/bin/sh
exec gunicorn app.main:api -b $API_BIND -k uvicorn.workers.UvicornWorker -w 4
