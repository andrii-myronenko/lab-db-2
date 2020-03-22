#!/usr/bin/env bash

if [[ ! -d venv ]]; then
    virtualenv venv --python=python3.6
    source venv/bin/activate
    pipenv install --dev
else
    source venv/bin/activate
fi
cd src
python main.py 2> /dev/null
