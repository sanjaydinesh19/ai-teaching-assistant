#!/usr/bin/env bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 2
