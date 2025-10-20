#!/usr/bin/env bash
set -ex

uvicorn backend.main:app --host 0.0.0.0 --port ${HTTP_PORT:-8000}
