#!/bin/bash

# Script to set up a Django project on Vagrant.

# Installation settings

PROJECT_NAME=$1

DB_NAME=$PROJECT_NAME
VIRTUALENV_NAME=$PROJECT_NAME

PROJECT_DIR=/home/vagrant/$PROJECT_NAME
VIRTUALENV_COMMAND=/home/vagrant/miniconda/bin/activate

PGSQL_VERSION=9.3

sudo yum update
sudo yum install -y git wget 
sudo yum groupinstall "Development tools" 
sudo yum install -y  vim mlocate
sudo yum  install -y xz zlib-devel bzip2-devel openssl openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel -y



if ! command -v psql; then
    num=`grep -c "postgres" /etc/yum.repos.d/CentOS-Base.repo`
    if [ "$num" -lt "1" ]; then sudo sed -i '19i19 exclude=postgresql*' /etc/yum.repos.d/CentOS-Base.repo ; sudo sed -i '28i28 exclude=postgresql*' /etc/yum.repos.d/CentOS-Base.repo ; fi
    curl -O http://yum.postgresql.org/9.3/redhat/rhel-6-x86_64/pgdg-centos93-9.3-1.noarch.rpm
    sudo rpm -ivh pgdg-centos93-9.3-1.noarch.rpm
    sudo yum install -y  postgresql93-server postgresql93-devel
    sudo service postgresql-9.3 initdb
    sudo chkconfig postgresql-9.3 on
    sudo ln -s /usr/pgsql-9.3/bin/pg_config /usr/bin/pg_config
fi

if ! command -v g++; then
    sudo   yum install gcc-c++ libxslt-devel libxml2-devel -y
fi

if ! command -v npm; then
    sudo rpm --import https://fedoraproject.org/static/0608B895.txt
    sudo rpm -Uvh http://download-i2.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
    sudo yum install npm --enablerepo=epel -y
fi

if ! command -v bower; then
    sudo npm install -g bower
fi
if ! command -v coffee; then
    sudo npm install -g coffee-script 
fi

if ! command -v lessc; then
    sudo npm install -g less
fi


cp -p $PROJECT_DIR/etc/install/bashrc /home/vagrant/.bashrc
sudo chown -R vagrant /home/vagrant
mkdir -p /home/vagrant/.pip_download_cache


sudo cp $PROJECT_DIR/etc/install/pg_hba.conf /var/lib/pgsql/9.3/data/
sudo /etc/init.d/postgresql-9.3 restart
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

wget http://repo.continuum.io/miniconda/Miniconda-3.5.5-Linux-x86_64.sh
chmod u+x Miniconda-3.5.5-Linux-x86_64.sh
./Miniconda-3.5.5-Linux-x86_64.sh -b

/home/vagrant/miniconda/bin/conda create -p /home/vagrant/miniconda/envs/$PROJECT_NAME python=2.7 --yes
source /home/vagrant/miniconda/bin/activate $PROJECT_NAME

sudo chown -R vagrant:vagrant   /home/vagrant/.pip_download_cache/
conda install pip --yes
conda install pandas --yes

pip install -r $PROJECT_NAME/requirements/local.txt

echo "source $VIRTUALENV_COMMAND $PROJECT_NAME" >> /home/vagrant/.bashrc