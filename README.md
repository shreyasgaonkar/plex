# Plex

Sometimes, when I have to setup my Plex server all over again (hardward failures, irreversible changes etc), I often have to go through my notes scattered all over the places, followed with extensive google search to find the missing pieces. Hopefully this will speed up the process for me in the future, or might help you along the way.

## Docker Installation

```shell
sudo yum update -y
sudo yum install -y docker
```

Setup Plex through Docker CLI:
> Assuming LVM volumes mounted at `/data1` and `/data2/` for Movies and TV shows

```shell
docker run -d \
  --name=plex \
  --net=host \
  -e PUID=1000 \
  -e PGID=1000 \
  -e VERSION=docker \
  -v /data1/plex/config:/config \
  -v /data2/tv_shows:/tv \
  -v /data1/plex/movies:/movies \
  --restart unless-stopped \
  lscr.io/linuxserver/plex:latest
```

### Initial Setup
Go to [localhost:32400/web](localhost:32400/web) and follow the Plex's onscreen instructions.


### Update Plex

```
docker restart linuxserver/plex
```

### Set file ownership and permissions
```shell
#### Set correct permissions
find /data1/plex/movies -type d -exec chmod 775 {} +;
find /data2/tv_shows -type d -exec chmod 775 {} +;

find /data1/plex/movies -type f -exec chmod 664 {} +;
find /data2/tv_shows -type f -exec chmod 664 {} +;

### Set ownership to plex:plex locally
sudo chown -R plex:plex /data1/plex/movies
sudo chown -R plex:plex /data2/tv_shows/

### Remove any `sample files`
find /data1/plex/movie -type f -name "Sample*" -exec rm {} +
find /data1/plex/movie -type f -name "sample*" -exec rm {} +
```

## Parse Plex files

Use [Plex filename parser using Python](https://github.com/shreyasgaonkar/Plex-filename-parser)


## Pull remote files locally
```shell

vim ~/.bashrc || vim ~/.zshrc # Select your shell from `echo $0`

export username="SFTP-USERNAME"
export password="SFTP-PASSWORD"
export server="SFTP-HOST"
```

Here, I want certain remote directories to be pulled in a certain local directories. First value in the tuple is the remote directory name and the second value is the `type` of the content. This is then used to find the local path using `LOCATION`. Change this as needed for your use-case.

```python
DIRS_TO_WATCH = [('auto', 'tv_shows'), ('completed', 'movies'),
                 ('tv_completed', 'tv_shows')]
LOCATION = {
    "tv_shows": '/data2/tv_shows',
    "movies": '/data1/plex/movies'
}
   
```

At the end when the entire directory is copied over, the script will remove the directory and move ahead.