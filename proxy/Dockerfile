FROM nginx:1.30.6-alpine AS builder

# Build the independent TLSFP/SYN module against unmodified nginx sources.
ARG CONNFP_REVISION=7d83cab08d1521df8a453c8b4fd0df9700a0f652
RUN apk add --no-cache build-base linux-headers openssl-dev pcre2-dev zlib-dev curl
WORKDIR /build
RUN curl -fsSL "https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz" -o nginx.tar.gz \
    && echo '3cf46f5ed7504d460125866b7bea99fb357f31d887e2e63b35503310e9b8b6c8  nginx.tar.gz' | sha256sum -c - \
    && curl -fsSL "https://codeload.github.com/nuclearcat/nginx-connfp/tar.gz/${CONNFP_REVISION}" -o connfp.tar.gz \
    && echo '1c5caf70e63f0fb3fefb4eb344b02efd192091ca80da8c7549bdfa8dbb7df774  connfp.tar.gz' | sha256sum -c - \
    && tar -xzf nginx.tar.gz \
    && mkdir connfp \
    && tar -xzf connfp.tar.gz -C connfp --strip-components=1
RUN cd "nginx-${NGINX_VERSION}" \
    && configure_args="$(nginx -V 2>&1 | sed -n 's/^configure arguments: //p')" \
    && eval "./configure ${configure_args} --add-module=/build/connfp" \
    && make -j4 \
    && cp objs/nginx /build/nginx

FROM nginx:1.30.6-alpine

# The stock debug binary lacks connfp variables. Keep the official entrypoint,
# envsubst support, log links and ABI-compatible stock dynamic modules.
RUN rm -f /usr/sbin/nginx-debug
COPY --from=builder /build/nginx /usr/sbin/nginx
COPY --from=builder /build/connfp/LICENSE /build/connfp/NOTICE /usr/share/licenses/nginx-connfp/

VOLUME ["/data/static"]

COPY etc/ /etc/
