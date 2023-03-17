FROM python:3.8.15-alpine

RUN apk update && apk add python3-dev gcc libc-dev
RUN apk --update --upgrade add gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install gunicorn
ADD ./requirements.txt /app/
RUN pip install -r requirements.txt

ADD ./project_x /app/project_x
ADD ./data /app/data

RUN chmod +x /app/data/backend/server-entrypoint.sh
RUN chmod +x /app/data/backend/worker-entrypoint.sh
