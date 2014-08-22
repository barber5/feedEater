import sys
import time
import fabric.exceptions
import boto.ec2
from fabric.api import *
from fabric.context_managers import cd



key_path = 'bundle.pem'

@task
def init_prod():
    env.key_filename = key_path
    conn = boto.ec2.connect_to_region('us-west-1')    
    for rsv in conn.get_all_instances(filters={'tag:Name': 'feedtest', 'instance-state-name':'running'}):
        for instance in rsv.instances:            
            print instance.tags['Name']
            env.host_string = 'ubuntu@%s' % instance.ip_address    
            print env.host_string
            sudo('echo \'deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main\' | sudo dd of=/etc/apt/sources.list.d/pgdg.list')
            sudo('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')        
            sudo('apt-get update')
            sudo('apt-get --yes install build-essential g++ curl libssl-dev apache2-utils')
            sudo('apt-get --yes install gcc autoconf bison flex libtool make libboost-all-dev libcurl4-openssl-dev curl libevent-dev memcached uuid-dev libsqlite3-dev libmysqlclient-dev libpq-dev postgresql-9.3')
            sudo('apt-get --yes install git-core')    
            sudo('apt-get --yes install python-setuptools')    
            sudo('easy_install pip')
            sudo('pip install redis')
            sudo('pip install psycopg2')
            sudo('pip install gearman')
            sudo('pip install boto')
            with settings(warn_only=True):
                result = run('node --version')
                if result.return_code != 0:
                    run('git clone https://github.com/joyent/node.git')
                    with cd('node'):
                        run('git checkout v0.10.24')
                        run('./configure')
                        run('make')
                        sudo('make install')                                           
            sudo('apt-get --yes install gearman-tools gearman redis-server')  
            sudo('npm install -g supervisor')  
            
            with cd('~/etheaConfig'):
                run('git fetch')
                run('git reset --hard origin/master')
            sudo('cp ~/etheaConfig/proddb/pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf')
            sudo('cp ~/etheaConfig/proddb/postgresql.conf /etc/postgresql/9.3/main/postgresql.conf')
            sudo('/etc/init.d/postgresql restart')

@task
def deploy(message='no message'):
    local('git add .')
    with settings(warn_only=True): 
        local('git commit -m "%s"' % message)
    local('git pull origin master && git push origin master')
    env.key_filename = key_path
    conn = boto.ec2.connect_to_region('us-west-1')    
    for rsv in conn.get_all_instances(filters={'tag:Name': 'feedtest', 'instance-state-name':'running'}):
        for instance in rsv.instances:     
            env.host_string = 'ubuntu@%s' % instance.ip_address                   
            with cd('feedEater'):                
                run('git fetch')
                run('git reset --hard origin/master')
                sudo('npm install')    
                with settings(warn_only=True): 
                    sudo('stop app')           
                    sudo('stop worker')
                sudo('start app')
                sudo('start worker')