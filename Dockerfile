FROM python:3.11-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /opt/areus

COPY backend/src/requirements.txt ./
COPY backend/scripts/start.sh ../
RUN chmod +x ../start.sh

RUN apk update && apk add gcc libc-dev g++

RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt

CMD [ "sh", "-c", "../start.sh" ]