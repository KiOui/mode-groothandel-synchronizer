#!/bin/sh

touch -a /log/uwsgi.log
touch -a /log/django.log

chown --recursive nobody:nogroup /log/

chown --recursive nobody:nogroup /app
python manage.py migrate --noinput

uwsgi --chdir=/app \
    --module=mode_groothandel.wsgi:application \
    --master --pidfile=/tmp/project-master.pid \
    --socket=:8000 \
    --processes=5 \
    --uid=nobody --gid=nogroup \
    --harakiri=20 \
    --post-buffering=16384 \
    --max-requests=5000 \
    --thunder-lock \
    --vacuum \
    --logfile-chown \
    --logto2=/log/uwsgi.log \
    --ignore-sigpipe \
    --ignore-write-errors \
    --disable-write-exception \
    --enable-threads \
    --py-call-uwsgi-fork-hooks \
    --buffer-size 32768