#!/bin/sh

VIRTUAL_ENV="env"

if [ ! -d "$VIRTUAL_ENV" ]; then
    echo "Creating virtual environment: env"
    python3 -m venv env
    source env/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "Done!"
fi