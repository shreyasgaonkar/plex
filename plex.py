#!/usr/bin/python3

import pysftp
import os

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
    print(files)
    for f in files:
        filepath = os.path.join(path, f)
        try:
            sftp.remove(filepath)
        except IOError:
            rm(filepath)

    sftp.rmdir(path)


with pysftp.Connection(server, username=username, password=password) as sftp:

    for dir, content_type in DIRS_TO_WATCH:

        remote_dir = f"/downloads/{dir}"
        local_dir = f"{LOCATION[content_type]}"

        sftp.chdir(remote_dir)
        print(f"Starting download from {remote_dir} to {local_dir}")

        try:
            sftp.get_r('.', local_dir)
            print(f"[Success] Copied dir: {remote_dir} to {local_dir}")
        except Exception as e:
            print(e)

        print(f"Removing all files under dir: {remote_dir}")
        print(rm(remote_dir))
        print(sftp.mkdir(remote_dir))