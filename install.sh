#!/bin/bash

## Install pipenv for virtualenv
echo "Install virtualenv"
python3 -m pip install pipenv --user

pipenv --python 3.6.8
pipenv install XRootD~=4.12.7
pipenv install babel


export LANG=ko_KR.utf8
pipenv shell
