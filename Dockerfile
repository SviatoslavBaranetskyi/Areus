FROM python:3.11-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /opt/areus

RUN apk update && apk add gcc libc-dev

COPY ./src/requirements.txt ./
COPY ./scripts/start.sh ../
RUN chmod +x ../start.sh

RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt

CMD [ "sh", "-c", "../start.sh" ]