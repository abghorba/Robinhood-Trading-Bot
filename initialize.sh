#!/bin/sh

if [ ! -d "env" ]; then
    echo "Creating virtual environment: env"
    python3 -m venv env
    source env/bin/activate
    echo "Upgrading pip..."
    python3 -m pip install --upgrade pip
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "Installing pre-commit hooks..."
    pre-commit install
    echo "Done!"
fi

TWITTER_CONSUMER_KEY=""
TWITTER_CONSUMER_SECRET=""
ROBINHOOD_USER=""
ROBINHOOD_PASS=""
ROBINHOOD_MFA_CODE=""
if [ ! -f ".env" ]; then
    echo "Creating .env file to store environment variables..."
    touch .env
    echo "TWITTER_CONSUMER_KEY = \"$TWITTER_CONSUMER_KEY\"" >> .env
    echo "TWITTER_CONSUMER_SECRET = \"$TWITTER_CONSUMER_SECRET\"" >> .env
    echo "ROBINHOOD_USER = \"$ROBINHOOD_USER\"" >> .env
    echo "ROBINHOOD_PASS = \"$ROBINHOOD_PASS\"" >> .env
    echo "ROBINHOOD_MFA_CODE = \"$ROBINHOOD_MFA_CODE\"" >> .env
    echo "Done!"
fi