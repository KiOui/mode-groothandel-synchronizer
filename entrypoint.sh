#!/bin/sh
chown -R nobody:nogroup /app/cache
python manage.py migrate --noinput
uwsgi --http :80 --wsgi-file /app/mode_groothandel/wsgi.py --master --processes 4 --threads 2 --uid nobody --gid nogroup --disable-logging --py-call-uwsgi-fork-hooks --enable-threads