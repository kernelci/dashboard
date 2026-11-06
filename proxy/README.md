# Proxy fingerprints

The image builds nginx 1.30.6 with the pinned
[nginx-connfp module](https://github.com/nuclearcat/nginx-connfp) for TLSFP and
Linux TCP SYN capture. No nginx core patches are needed. Source archives are checked
against SHA-256 hashes. Keep both image versions, source hashes and the module
revision in `Dockerfile` in sync when updating them.

The official image's entrypoint, template substitution and stdout/stderr log
links remain in use. Stock dynamic modules remain ABI-compatible. The stock
debug binary is removed because it does not include the connfp variables.

## Configuration and logs

The default template serves HTTP on port 80 and HTTPS on port 443. Mount the
certificate chain at `/etc/nginx/ssl/fullchain.pem` and its key at
`/etc/nginx/ssl/privkey.pem`, as the deployment Compose files already do. Publish
port 443 when terminating public TLS here. The development template replaces
this server with an HTTP-only proxy and does not require certificates.

Public access logs are JSON on stdout. `tlsfp` describes the TLS ClientHello
using [ntop TLSFP draft 0.1](https://github.com/ntop/nDPI/blob/a01ea9463125b24dcf7b37d71274291dc4a95753/fingerprint/nDPI_TLS_Fingerprint.md).
`tlsfp_registry` records ephemeral extension registry version `1`. `tcp_syn`
uses connfp's `syn1:ip_version:ttl_or_hop_limit:df:window:mss:window_scale:option_kinds`
format. For example, `syn1:4:64:1:64240:1460:7:2-4-8-1-3`. Missing MSS, window
scale or options use `-`; IPv6 has no DF bit and uses `-` there.
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

The module is independently implemented under BSD-2-Clause. Its license and
ntop specification attribution are included at `/usr/share/licenses/nginx-connfp/`.
It contains no FoxIO module source or patches. `tcp_save_syn` and the two legacy
nginx variables `$http_ssl_ja4` and `$http_ssl_ja4t` remain accepted as aliases,
but values use TLSFP and `syn1:`. Log consumers must migrate the old `tls_ja4`
and `tcp_ja4t` keys and their expected formats to `tlsfp` and `tcp_syn`.

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
