#!/usr/bin/python3

import pysftp
import pysftp.exceptions
import os
import time
from stat import S_ISDIR, S_ISREG

# Disable host key requirement for pysftp for cronjobs
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

server = os.environ.get("server")
username = os.environ.get("username")
password = os.environ.get("password")


### Global configs
MAX_RETRIES = 3
SLEEP_SECONDS = 90

# Map of media type and local directory path
LOCATION = {"tv_shows": "/data2/tv_shows", "movies": "/data1/plex/movies"}

# Map of remote directory location and it's corresponding local media location
DIRS_TO_WATCH = [
    ("/downloads/auto", LOCATION["tv_shows"]),
    ("/downloads/completed", LOCATION["movies"]),
    ("/downloads/tv_completed", LOCATION["tv_shows"]),
]

### End global configs


def rm(path, sftp):
    """Remove remote directory"""

    files = sftp.listdir(path)
    for f in files:
        filepath = os.path.join(path, f)
        try:
            sftp.remove(filepath)
        except IOError:
            rm(filepath, sftp)
    sftp.rmdir(path)


def remove_file(directory_name, file_name, sftp):
    """Remove remote file"""
    sftp.remove(os.path.join(directory_name, file_name))
    return


def download_and_delete_dir(dir_name, local_dir, remote_dir, sftp):
    """Download and initiate directory removal"""
    print(f"└── Downloading dir: {dir_name}")

    try:
        sftp.get_r(".", local_dir)
        print(f"└── 💾  Copied dir: {remote_dir}/{dir_name} to {local_dir}")
        print(rm(dir_name, sftp))
        print(f"└── 🗑️  Deleted dir: {dir_name}")
    except Exception as e:
        print(e)


def download_and_delete_file(file_name, directory_name, local_dir, sftp):
    """Download and initiate file removal"""
    print(f"└── Downloading file: {file_name}")

    if file_name.endswith(".meta"):
        remove_file(directory_name, file_name, sftp)
        print(f"⏭️  Skipped and deleted: {file_name}")
        return

    try:
        sftp.get_r(".", local_dir)
        print(f"└── 💾  Copied file: {directory_name}/{file_name} to {local_dir}")
        # sftp.remove(os.path.join(directory_name, file_name))
        remove_file(directory_name, file_name, sftp)
        print(f"└── 🗑️  Deleted dir: {directory_name}")
    except Exception as e:
        print(e)


def get_data():
    """Connect to remove server to download files and directories"""
    with pysftp.Connection(
        host=server, username=username, password=password, cnopts=cnopts
    ) as sftp:
        for remote_dir, local_dir in DIRS_TO_WATCH:
            sftp.chdir(remote_dir)
            print(f"Listing dir: {remote_dir}")

            for entry in sftp.listdir_attr():
                mode = entry.st_mode
                if S_ISDIR(mode):
                    download_and_delete_dir(entry.filename, local_dir, remote_dir, sftp)
                elif S_ISREG(mode):
                    download_and_delete_file(
                        entry.filename, remote_dir, local_dir, sftp
                    )
                    # print(entry.filename + " is file")


def main():
    """Main function"""
    for _ in range(MAX_RETRIES):
        try:
            get_data()
            break
        except pysftp.exceptions.ConnectionException:
            time.sleep(SLEEP_SECONDS)
        except Exception as exp:
            print(f"Unknown exception: {exp}")


if __name__ == "__main__":
    main()
