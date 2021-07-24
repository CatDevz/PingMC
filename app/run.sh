#!/bin/sh
exec gunicorn main:api -b $API_BIND -k uvicorn.workers.UvicornWorker -w 4
