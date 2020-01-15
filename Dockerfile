FROM python:3-alpine

LABEL maintainer="sabbe.jonathan@gmail.com"

WORKDIR /app

COPY ./conf ./conf
COPY ./*.py ./requirements.txt ./
COPY ./start.sh /

RUN apk add -U curl && \
    apk upgrade && \
    curl -L -o /wait https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.2/wait && \
    chmod +x /wait /start.sh && \
    pip install --no-cache-dir -r ./requirements.txt

ENTRYPOINT ["/start.sh"]
