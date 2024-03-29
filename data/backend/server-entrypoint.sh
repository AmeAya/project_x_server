#!/bin/sh

until cd /app/project_x
do
    echo "Waiting for server volume..."
done

python manage.py makemigrations project
python manage.py makemigrations

until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done

until python manage.py loaddata data.json
do
    echo "Waiting for load backups..."
    sleep 2
done

python manage.py collectstatic --noinput

gunicorn main.wsgi --bind 0.0.0.0:8000 --workers 4 --threads 4

# for debug
python manage.py runserver 0.0.0.0:8000
