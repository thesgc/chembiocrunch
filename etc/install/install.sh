#!/bin/bash

# Script to set up a Django project on Vagrant.

# Installation settings

PROJECT_NAME=$1

DB_NAME=$PROJECT_NAME
VIRTUALENV_NAME=$PROJECT_NAME

PROJECT_DIR=/home/vagrant/$PROJECT_NAME
VIRTUALENV_DIR=/home/vagrant/.virtualenvs/$PROJECT_NAME

PGSQL_VERSION=9.3


cp -p $PROJECT_DIR/etc/install/bashrc /home/vagrant/.bashrc
sudo chown -R vagrant /home/vagrant
mkdir -p /home/vagrant/.pip_download_cache
mkdir -p /home/vagrant/.virtualenvs
mkdir -p $VIRTUALENV_DIR
/usr/local/bin/virtualenv $VIRTUALENV_DIR && \
    echo $PROJECT_DIR > $VIRTUALENV_DIR/.project && \
    PIP_DOWNLOAD_CACHE=/home/vagrant/.pip_download_cache $VIRTUALENV_DIR/bin/pip install -r $PROJECT_DIR/requirements.txt
sudo $VIRTUALENV_DIR/bin/pip install -r $PROJECT_DIR/requirements/local.txt

echo "workon $VIRTUALENV_NAME" >> /home/vagrant/.bashrc

sudo cp $PROJECT_DIR/etc/install/pg_hba.conf /var/lib/pgsql/9.3/data/
sudo /etc/init.d/postgresql-9.3 reload
createdb -Upostgres $DB_NAME



wget --no-check-certificate --no-cookies - --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/7u60-b19/jdk-7u60-linux-x64.rpm
sudo rpm -Uvh jdk-7u60-linux-x64.rpm

ln -s   /usr/java/jdk1.7.0_60/bin/java /etc/alternatives/java
# ln -s  /etc/alternatives/java /usr/bin/java

sudo echo "JAVA_HOME=/usr/java/jdk1.7.0_60/jre
PATH=$PATH:$JAVA_HOME/bin
export JAVA_HOME
export PATH" >> /etc/profile
source /etc/profile


sudo rpm --import http://packages.elasticsearch.org/GPG-KEY-elasticsearch
sudo echo "[elasticsearch-1.2]
name=Elasticsearch repository for 1.2.x packages
baseurl=http://packages.elasticsearch.org/elasticsearch/1.2/centos
gpgcheck=1
gpgkey=http://packages.elasticsearch.org/GPG-KEY-elasticsearch
enabled=1" > /etc/yum.repos.d/elasticsearch.repo

sudo yum install elasticsearch

sudo /sbin/chkconfig --add elasticsearch


# Set execute permissions on manage.py, as they get lost if we build from a zip file
# chmod a+x $PROJECT_DIR/manage.py

# # Django project setup
# su - vagrant -c "source $VIRTUALENV_DIR/bin/activate && cd $PROJECT_DIR && ./manage.py syncdb --noinput && ./manage.py migrate"

# sudo yum install devtoolset-1.1-gcc  devtoolset-1.1-gcc-c++
# sudo unlink /usr/bin/gcc
# sudo ln -s /opt/centos/devtoolset-1.1/root/usr/bin/gcc /usr/bin/gcc
# 
# easy_install-2.7 -i http://pypi.douban.com/simple pip



# Need to fix locale so that Postgres creates databases in UTF-8
# cp -p $PROJECT_DIR/etc/install/etc-bash.bashrc /etc/bash.bashrc
# locale-gen en_GB.UTF-8
# dpkg-reconfigure locales

# export LANGUAGE=en_GB.UTF-8
# export LANG=en_GB.UTF-8
# export LC_ALL=en_GB.UTF-8

# # Install essential packages from Apt
# apt-get update -y
# # Python dev packages
# apt-get install -y build-essential python python-dev
# # python-setuptools being installed manually
# wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python
# # Dependencies for image processing with Pillow (drop-in replacement for PIL)
# # supporting: jpeg, tiff, png, freetype, littlecms
# # (pip install pillow to get pillow itself, it is not in requirements.txt)
# apt-get install -y libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev
# # Git (we'd rather avoid people keeping credentials for git commits in the repo, but sometimes we need it for pip requirements that aren't in PyPI)
# apt-get install -y git

# # Postgresql
# if ! command -v psql; then
#     apt-get install -y postgresql-$PGSQL_VERSION libpq-dev
#     
#     /etc/init.d/postgresql reload
# fi

# # virtualenv global setup
# if ! command -v pip; then
#     easy_install -U pip
# fi
# if [[ ! -f /usr/local/bin/virtualenv ]]; then
#     pip install virtualenv virtualenvwrapper stevedore virtualenv-clone
# fi

# # bash environment global setup
# cp -p $PROJECT_DIR/etc/install/bashrc /home/vagrant/.bashrc
# su - vagrant -c "mkdir -p /home/vagrant/.pip_download_cache"

# # Node.js, CoffeeScript and LESS
# if ! command -v npm; then
#     wget http://nodejs.org/dist/v0.10.0/node-v0.10.0.tar.gz
#     tar xzf node-v0.10.0.tar.gz
#     cd node-v0.10.0/
#     ./configure && make && make install
#     cd ..
#     rm -rf node-v0.10.0/ node-v0.10.0.tar.gz
# fi
# if ! command -v coffee; then
#     npm install -g coffee-script
# fi
# if ! command -v lessc; then
#     npm install -g less
# fi

# # ---

# # postgresql setup for project
# createdb -Upostgres $DB_NAME

# # virtualenv setup for project

