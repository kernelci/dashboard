FROM alpine:3.20

RUN export LANG=en_US.UTF-8 \
    && apk update \
    && apk upgrade \
    && apk add rsync \
    && rm -rf /var/cache/apk/*

WORKDIR /data

VOLUME ["/data/static/"]

COPY --from=dashboard:latest /dashboard/dist /files

CMD rsync -azvi --checksum --exclude='*.map' /files/ /data/static/
