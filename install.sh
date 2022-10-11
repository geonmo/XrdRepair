#!/bin/bash

## Install pipenv for virtualenv
echo "Install virtualenv"
python3 -m pip install pipenv --user

pipenv --python 3.6.8

export LANG=ko_KR.utf8
pipenv shell
