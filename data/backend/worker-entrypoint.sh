#!/bin/sh

until cd /app/project_x
do
    echo "Waiting for server volume..."
done

# run a worker :)
celery -A main worker --loglevel=info --concurrency 1 -E
