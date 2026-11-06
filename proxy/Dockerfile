FROM nginx:1.30.6-alpine AS builder

# Pin both sources: the module changes nginx's connection structs, so its
# ClientHello and SYN patches must be built into nginx, not loaded dynamically.
ARG JA4_REVISION=50bd33092d819c8145b677acc28112c62449692b
RUN apk add --no-cache build-base linux-headers openssl-dev pcre2-dev zlib-dev curl patch
WORKDIR /build
RUN curl -fsSL "https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz" -o nginx.tar.gz \
    && echo '3cf46f5ed7504d460125866b7bea99fb357f31d887e2e63b35503310e9b8b6c8  nginx.tar.gz' | sha256sum -c - \
    && curl -fsSL "https://api.github.com/repos/FoxIO-LLC/ja4-nginx-module/tarball/${JA4_REVISION}" -o ja4.tar.gz \
    && echo '01ab8b4a2ae4a319424f32756bc76f2b61a6c7645207bf8af0476a9280d84c0a  ja4.tar.gz' | sha256sum -c - \
    && tar -xzf nginx.tar.gz \
    && mkdir ja4 \
    && tar -xzf ja4.tar.gz -C ja4 --strip-components=1
RUN cd "nginx-${NGINX_VERSION}" \
    && patch -p1 < ../ja4/patches/nginx-ssl-save-client-hello.patch \
    && patch -p1 < ../ja4/patches/nginx-tcp-save-syn.patch \
    && configure_args="$(nginx -V 2>&1 | sed -n 's/^configure arguments: //p')" \
    && eval "./configure ${configure_args} --add-module=/build/ja4" \
    && make -j4 \
    && cp objs/nginx /build/nginx

FROM nginx:1.30.6-alpine

# Stock dynamic modules and the debug binary have a different ABI from the
# patched binary. Keep the official entrypoint, envsubst support and log links.
RUN rm -f /usr/lib/nginx/modules/*.so /usr/sbin/nginx-debug
COPY --from=builder /build/nginx /usr/sbin/nginx
COPY --from=builder /build/ja4/LICENSE /usr/share/licenses/ja4-nginx-module/LICENSE

VOLUME ["/data/static"]

COPY etc/ /etc/
