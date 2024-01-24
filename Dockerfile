FROM python:3.8-alpine

WORKDIR /areus

RUN apk update && apk add gcc libc-dev

COPY ./src/requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "areus.wsgi:application" ]