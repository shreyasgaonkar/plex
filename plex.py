#!/usr/bin/python3

import pysftp
import os

# Disable host key requirement for pysftp for cronjobs
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

server = os.environ.get("server")
username = os.environ.get("username")
password = os.environ.get("password")

DIRS_TO_WATCH = [("auto", "tv_shows"), ("completed", "movies"),
                 ("tv_completed", "tv_shows")]
LOCATION = {
    "tv_shows": "/data2/tv_shows",
    "movies": "/data1/plex/movies"
}


def rm(path):
    files = sftp.listdir(path)
    for f in files:
        filepath = os.path.join(path, f)
        try:
            sftp.remove(filepath)
        except IOError:
            rm(filepath)
    sftp.rmdir(path)


def download_and_delete_dir(dir_name, local_dir):
    print(f"Downloading dir: {dir_name}")

    try:
        sftp.get_r('.', local_dir)
        print(f"[Success] Copied dir: {dir_name} to {local_dir}")
        print(rm(dir_name))
        print(f"[Success] Deleted dir: {dir_name}")
    except Exception as e:
        print(e)


with pysftp.Connection(server, username=username, password=password, cnopts=cnopts) as sftp:

    for dir, content_type in DIRS_TO_WATCH:

        remote_dir = f"/downloads/{dir}"
        local_dir = f"{LOCATION[content_type]}"

        sftp.chdir(remote_dir)
        print(f"Listing dir: {remote_dir}")
        all_dirs = sftp.listdir()

        for single_dir in all_dirs:
            download_and_delete_dir(single_dir, local_dir)
