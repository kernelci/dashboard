# Proxy fingerprints

The image builds nginx 1.30.6 with the pinned
[FoxIO JA4 module](https://github.com/FoxIO-LLC/ja4-nginx-module), its ClientHello
capture patch and its Linux TCP SYN capture patch. Source archives are checked
against SHA-256 hashes. Keep both image versions, source hashes and the module
revision in `Dockerfile` in sync when updating them.

The official image's entrypoint, template substitution and stdout/stderr log
links remain in use. Stock dynamic modules and the stock debug binary are
removed because the patches change nginx's ABI. Any additional module must be
built against these same patched sources.

## Configuration and logs

The default template serves HTTP on port 80 and HTTPS on port 443. Mount the
certificate chain at `/etc/nginx/ssl/fullchain.pem` and its key at
`/etc/nginx/ssl/privkey.pem`, as the deployment Compose files already do. Publish
port 443 when terminating public TLS here. The development template replaces
this server with an HTTP-only proxy and does not require certificates.

Public access logs are JSON on stdout. `tls_ja4` describes the TLS ClientHello;
`tcp_ja4t` contains the SYN window size, TCP option order, MSS and window scale.
The format also records the request, status, bytes, timing, user agent, peer
address/port, request ID, connection ID, negotiated TLS version, cipher and ALPN.
Client-supplied fingerprint headers are ignored. The internal port 8080 keeps
the original access-log format and does not collect SYNs, so its Anubis
connections are not mistaken for public-client fingerprints. Log consumers
must handle the public JSON records alongside these internal combined records.

Capture must happen where the original connection arrives. If another proxy
terminates TCP or TLS first, these fields describe that proxy or are unavailable;
`X-Forwarded-For` cannot restore the original handshakes. Plain HTTP has no TLS
fingerprint. SYN fingerprints can be unavailable with SYN cookies or unsupported
kernels, and HTTP/3 has no TCP SYN. Empty strings or `-` mean unknown, not trusted.
The current listeners do not enable HTTP/3.

This adds logging only; Anubis policy is unchanged. Fingerprints are shared by
many clients and can be imitated. They are not unique identities.

The module uses the [FoxIO License 1.1](https://github.com/FoxIO-LLC/ja4-nginx-module/blob/50bd33092d819c8145b677acc28112c62449692b/LICENSE),
which is distinct from nginx's license and includes restrictions on commercial
use and distribution. The image includes it at
`/usr/share/licenses/ja4-nginx-module/LICENSE`.

## Local verification

On a Linux Docker host with Python 3, OpenSSL and curl with HTTP/2 support installed,
run from the repository root:

```sh
docker build -t dashboard-proxy:fingerprints ./proxy
python3 proxy/test-fingerprints.py dashboard-proxy:fingerprints
```

The script uses ephemeral certificates, loopback-only randomly allocated ports,
an isolated Docker network, the repository's Anubis policy and a small backend
stub. It checks actual access-log values for HTTP, TLS 1.2 and TLS 1.3, connection
reuse, forged fingerprint headers, JSON escaping, static/API routing through
Anubis and the certificate-free development override. It prints the TLS/SYN
records, checks HTTP/2 negotiation, and removes its containers, volumes and network
when finished.
