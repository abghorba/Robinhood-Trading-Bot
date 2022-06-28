#!/bin/sh

git init
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt