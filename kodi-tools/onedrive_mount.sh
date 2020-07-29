#!/bin/bash

# LOG文件
log='/mnt/sda2/log/onedrive_mount.log'

rclone mount od:"Shared Media/剧情" /mnt/sda2/emby/tvshow --copy-links --no-gzip-encoding --no-check-certificate --allow-other --allow-non-empty --umask 000 --daemon --log-file=${log} --log-level INFO
rclone mount od:"Shared Media/电影" /mnt/sda2/emby/movie --copy-links --no-gzip-encoding --no-check-certificate --allow-other --allow-non-empty --umask 000 --daemon --log-file=${log} --log-level INFO
rclone mount od:"Shared Gallery" /mnt/sda2/emby/gallery --copy-links --no-gzip-encoding --no-check-certificate --allow-other --allow-non-empty --umask 000 --daemon --log-file=${log} --log-level INFO
rclone mount od:"Shared Media/tools" /mnt/sda2/emby/tools --copy-links --no-gzip-encoding --no-check-certificate --allow-other --allow-non-empty --umask 000 --daemon --log-file=${log} --log-level INFO