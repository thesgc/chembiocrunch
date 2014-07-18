#!/bin/bash

# Script to set up a Django project on Vagrant.

# Installation settings

PROJECT_NAME=$1

DB_NAME=$PROJECT_NAME
VIRTUALENV_NAME=$PROJECT_NAME

PROJECT_DIR=/home/vagrant/$PROJECT_NAME
VIRTUALENV_COMMAND=/home/vagrant/miniconda/bin/activate


source /home/vagrant/miniconda/bin/activate $PROJECT_NAME

sudo chown -R vagrant:vagrant   /home/vagrant/.pip_download_cache/
conda install pip --yes
conda install pandas --yes

pip install -r $PROJECT_NAME/requirements/local.txt

echo "source $VIRTUALENV_COMMAND $PROJECT_NAME" >> /home/vagrant/.bashrc