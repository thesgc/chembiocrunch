PROJECT_NAME=$1

DB_NAME=$PROJECT_NAME
VIRTUALENV_NAME=$PROJECT_NAME

PROJECT_DIR=/home/vagrant/$PROJECT_NAME
VIRTUALENV_DIR=/home/vagrant/.virtualenvs/$PROJECT_NAME

PGSQL_VERSION=9.3

sudo yum update
sudo yum install -y git wget 
sudo yum groupinstall "Development tools" 
sudo yum install -y  vim mlocate
sudo yum  install xz zlib-devel bzip2-devel openssl openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel -y


if ! command -v python2.7; then
    wget http://python.org/ftp/python/2.7.6/Python-2.7.6.tar.xz 

    tar xf Python-2.7.6.tar.xz
    cd Python-2.7.6
    ./configure --prefix=/usr/local --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
    sudo make && sudo make altinstall
    cd ..
fi
# wget --no-check-certificate https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.9.1.tar.gz#md5=07e09df0adfca0b2d487e39a4bf2270a
# tar -xvzf virtualenv-1.9.1.tar.gz 

#sudo /usr/local/bin/python2.7 virtualenv-1.9.1/setup.py  install

if ! command -v easy_install-2.7; then
    wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
fi
if ! command -v pip2.7; then
    sudo /usr/local/bin/python2.7 ez_setup.py
    sudo /usr/local/bin/easy_install-2.7 -i http://pypi.douban.com/simple pip
fi

sudo /usr/local/bin/pip2.7 install virtualenv virtualenvwrapper
mkdir /home/vagrant/.virtualenvs -p


cp -p $PROJECT_DIR/etc/install/bashrc /home/vagrant/.bashrc
sudo su - vagrant -c "mkdir -p /home/vagrant/.pip_download_cache"

# echo 'export WORKON_HOME=/home/vagrant/.virtualenvs' >> /home/vagrant/.bashrc
# source /home/vagrant/.bashrc
# mkdir -p $WORKON_HOME
# echo 'export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python2.7'  >> /home/vagrant/.bashrc
# echo '. /usr/local/bin/virtualenvwrapper.sh' >> /home/vagrant/.bashrc
# source /home/vagrant/.bashrc
# mkvirtualenv "$VIRTUALENV_NAME"
# echo "workon $VIRTUALENV_NAME" >> /home/vagrant/.bashrc
# source /home/vagrant/.bashrc

# Postgresql
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



