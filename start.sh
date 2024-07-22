#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Start Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
