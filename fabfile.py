import random

from fabric.api import cd, env, run, local, sudo
from fabric.contrib.files import exists, append

REPO_URL = 'https://github.com/alice-njoroge/RATSTParserAPI.git'


def deploy():
    env.use_ssh_config = True
    site_folder = f'/home/nanoafrika/RATSTParserAPI'
    run(f'mkdir  -p {site_folder}')
    with cd(site_folder):
        _get_latest_source()
        _update_main_virtualenv()
        _create_main_server_folders()
        _create_main_webserver_files()
        _restart_main_server()


def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git init')
        run(f'git remote add origin {REPO_URL}')
        run('git fetch')
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f'git reset --hard {current_commit}')


def _update_main_virtualenv():
    if not exists('venv/bin/pip'):
        run(f'python3.6 -m venv venv')
    run('./venv/bin/pip install --upgrade pip')
    run('./venv/bin/pip install -r requirements.txt')


def _create_main_server_folders():
    run(f'mkdir  -p /home/nanoafrika/logs')


def _create_main_webserver_files():
    if not exists('/etc/nginx/sites-available/ratst_api'):
        run('touch /home/nanoafrika/logs/ratst_api.log')
        sudo('cp ratst_api.conf /etc/supervisor/conf.d/')
        sudo('supervisorctl reread')
        sudo('supervisorctl update')
        sudo('supervisorctl status ratstapi')
        sudo('cp nginx.template.conf /etc/nginx/sites-available/ratst_api')
        sudo('ln -s /etc/nginx/sites-available/ratst_api /etc/nginx/sites-enabled/ratst_api')
        sudo('service nginx restart')


def _restart_main_server():
    sudo('supervisorctl restart ratstapi')
