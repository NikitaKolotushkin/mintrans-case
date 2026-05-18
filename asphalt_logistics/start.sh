#!/bin/sh

uvicorn app.main:app --host 0.0.0.0 --port ${LOGISTICS_SERVICE_PORT} --reload
