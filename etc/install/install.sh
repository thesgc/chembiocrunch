#!/bin/bash

# Script to set up a Django project on Vagrant.

# Installation settings

PROJECT_NAME=$1

DB_NAME=$PROJECT_NAME
VIRTUALENV_NAME=$PROJECT_NAME

PROJECT_DIR=/home/vagrant/$PROJECT_NAME
VIRTUALENV_COMMAND=/home/vagrant/miniconda/bin/activate


source /home/vagrant/miniconda/bin/activate $PROJECT_NAME

cp -p $PROJECT_DIR/etc/install/bashrc /home/vagrant/.bashrc

sudo chown -R vagrant:vagrant   /home/vagrant/.pip_download_cache/
conda install pip --yes
conda install pandas --yes
conda install pytables --yes
conda install psycopg2 --yes
pip install -r $PROJECT_NAME/requirements/local.txt
