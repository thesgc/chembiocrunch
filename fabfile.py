from __future__ import with_statement
from fabric.api import local
from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['chembiohub.ox.ac.uk']

def _deploy(code_dir, process_name):
    # with settings(warn_only=True):
    #     if run("test -d %s" % code_dir).failed:
    #         run("git clone user@vcshost:/path/to/repo/.git %s" % code_dir)
    with cd(code_dir):          
        sudo("git pull")        
        sudo("supervisorctl reread")
        sudo("supervisorctl reload")
        sudo("/etc/init.d/httpd reload")



def deploy():
    _deploy("/var/www/chembiocrunch/", "chem_bio_crunch")


def prep():
    local("git add -p && git commit")
    local("git push")


