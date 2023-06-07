ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-alpine

ARG BUILD_DATE

LABEL maintainer="sabbe.jonathan@gmail.com"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.build-date="${BUILD_DATE}"

WORKDIR /app

COPY ./src/app/*.py ./requirements.txt ./
COPY ./start.sh /usr/local/bin

RUN apk add -U curl \
    && apk upgrade \
    && curl -L -o /wait https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait \
    && chmod +x /wait /usr/local/bin/start.sh \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r ./requirements.txt \
    && adduser -H bnppf -D \
    && chown -R bnppf:bnppf .

USER bnppf

ENV TZ="Europe/Brussels" \
    SLEEP="10" \
    CSV_TODO="./todo" \
    CSV_DONE="./done" \
    CSV_ERROR="./error" \
    DB_HOST="localhost" \
    DB_NAME="BNPPF" \
    DB_PORT=3306 \
    DB_PASSWORD="" \
    DB_USER="bnppf"

ENTRYPOINT [ "/usr/local/bin/start.sh" ]

CMD [ "python", "main.py" ]
