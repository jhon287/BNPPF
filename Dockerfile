FROM python:3-alpine

WORKDIR /app

RUN apk add -U curl && \
    apk upgrade && \
    curl -L -o /wait https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.2/wait

COPY ./conf ./conf
COPY ./banking.py ./requirements.txt ./
COPY ./start.sh /

RUN chmod +x /wait /start.sh && pip install --no-cache-dir -r ./requirements.txt

ENTRYPOINT ["/start.sh"]
