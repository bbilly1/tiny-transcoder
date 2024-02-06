# build python requirements
FROM python:3.11.6-slim-bookworm AS python-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential

COPY ./requirements.txt /requirements.txt
RUN pip install --user -r requirements.txt

# build main.js
FROM node:20.5 AS js-builder

RUN mkdir /app
WORKDIR /app
COPY ./app/package.json .
RUN npm install

COPY ./app .
RUN npx webpack --config webpack.config.js

# build final image
FROM python:3.11.6-slim-bookworm as transcoder

ARG INSTALL_DEBUG
ENV PYTHONUNBUFFERED 1

# install debug tools for testing environment
RUN if [ "$INSTALL_DEBUG" ] ; then \
        apt-get -y update && apt-get -y install --no-install-recommends \
        vim htop bmon net-tools iputils-ping procps curl \
        && pip install --user ipython \
    ; fi

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /data /cache /app

# copy build requirements
COPY --from=python-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY ./app /app

# copy compiled js
COPY --from=js-builder \
    /app/static/dist \
    /app/static/dist

# volumes
VOLUME /data
VOLUME /media
VOLUME /cache

# start
WORKDIR /app

CMD ["./run.sh"]
