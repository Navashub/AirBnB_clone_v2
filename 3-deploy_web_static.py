#!/usr/bin/python3
"""Distributes an archive to your web servers"""
import os
from fabric.api import *
from datetime import datetime


def do_pack():
    """Create a tar gzipped archive of the directory web_static"""
    try:
        dt = datetime.now()
        file_name = "versions/web_static_{}{}{}{}{}{}.tgz".format(dt.year,
                                                                  dt.month,
                                                                  dt.day,
                                                                  dt.hour,
                                                                  dt.minute,
                                                                  dt.second)
        if not os.path.isdir("versions"):
            local("mkdir versions")

        local("tar -cvzf {} web_static/*".format(file_name))
        return file_name
    except Exception:
        return None


env.hosts = ['100.26.171.136', '54.197.82.190']


def do_deploy(archive_path):
    """deploys the archive to the servers and updates it"""
    if not os.path.isfile(archive_path):
        return False

    try:
        # Upload the archive to the /tmp/ directory of the web server
        put(archive_path, '/tmp/')

        # Uncompress the archive to the folder
        # /data/web_static/releases/<archive filename without extension>
        # on the web server
        filename = os.path.basename(archive_path)
        fname = filename.split('.')[0]
        folder_name = '/data/web_static/releases/' + fname
        run('mkdir -p {}'.format(folder_name))
        run('tar -xzf /tmp/{} -C {}'.format(filename, folder_name))

        # Delete the archive from the web server
        run('rm /tmp/{}'.format(filename))

        # Move content out of the sub-folder
        run("mv /data/web_static/releases/{}/web_static/*\
            /data/web_static/releases/{}/".format(fname, fname))

        # Delete the symbolic link /data/web_static/current from the web server
        run('rm -rf /data/web_static/current')

        # Create a new the symbolic link /data/web_static/current on the
        # web server linked to the new version of your code
        # (/data/web_static/releases/<archive filename without extension>)
        run('ln -s {} /data/web_static/current'.format(folder_name))

        return True
    except Exception:
        return False


def deploy():
    """Creates and distributes an archive to your web servers"""
    path = do_pack()
    if not path:
        return False
    return do_deploy(path)
