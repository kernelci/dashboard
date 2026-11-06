#!/usr/bin/env python3
"""Exercise the built proxy through Anubis, without starting the dashboard stack."""

import http.client
import json
from pathlib import Path
import re
import ssl
import subprocess
import sys
import tempfile
import time
import uuid


IMAGE = sys.argv[1] if len(sys.argv) > 1 else "dashboard-proxy:fingerprints"
ROOT = Path(__file__).resolve().parents[1]
NETWORK = f"dashboard-fingerprint-test-{uuid.uuid4().hex[:8]}"
CONTAINERS = []
USER_AGENT = 'curl/fingerprint-test "quoted" \\ escaped'


def docker(*args):
    return subprocess.check_output(["docker", *args], text=True).strip()


def start(role, *args):
    name = f"{NETWORK}-{role}"
    docker("run", "-d", "--name", name, "--network", NETWORK, *args)
    CONTAINERS.append(name)
    return name


def port(name, container_port):
    return int(docker("port", name, str(container_port)).rsplit(":", 1)[1])


def wait_ready(name, container_port):
    for _ in range(100):
        try:
            connection = http.client.HTTPConnection("localhost", port(name, container_port), timeout=1)
            connection.request("GET", "/", headers={"User-Agent": "curl/readiness"})
            response = connection.getresponse()
            body = response.read()
            connection.close()
            if response.status == 200 and body == b"fingerprint-test\n":
                return
        except (OSError, http.client.HTTPException):
            pass
        time.sleep(0.1)
    raise AssertionError(f"Proxy did not become ready: {docker('logs', name)}")


def request(connection, path):
    connection.request("GET", path, headers={
        "User-Agent": USER_AGENT,
        # These names overlap the module's variables. They must never supply
        # fingerprints, even on plain HTTP where JA4 is unavailable.
        "SSL-JA4": "forged-tls",
        "SSL-JA4T": "forged-tcp",
    })
    response = connection.getresponse()
    body = response.read()
    assert response.status == 200, (path, response.status, body)
    assert body == b"fingerprint-test\n", (path, body)


def records(name, expected_paths):
    for _ in range(50):
        rows = [json.loads(line) for line in docker("logs", name).splitlines() if line.startswith("{")]
        selected = {row["request"].split()[1]: row for row in rows
                    if row["request"].split()[1] in expected_paths}
        if selected.keys() == expected_paths:
            return selected
        time.sleep(0.1)
    raise AssertionError(f"Missing access logs: {expected_paths - selected.keys()}")


def check_common(row):
    assert row["status"] == 200, row
    assert row["user_agent"] == USER_AGENT, row
    assert re.fullmatch(r"\d+_[\d-]+_\d+_\d+", row["tcp_ja4t"]), row
    assert re.fullmatch(r"[0-9a-f]{32}", row["request_id"]), row


def main():
    with tempfile.TemporaryDirectory(prefix="dashboard-fingerprints-") as temporary:
        directory = Path(temporary)
        # nginx workers need to traverse the bind-mounted static directory.
        directory.chmod(0o755)
        (directory / "index.html").write_text("fingerprint-test\n")
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
            "-keyout", str(directory / "privkey.pem"), "-out", str(directory / "fullchain.pem"),
            "-days", "1", "-subj", "/CN=localhost",
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        (directory / "backend.conf").write_text(
            "events {} http { server { listen 8000; listen 5173; "
            "location / { return 200 'fingerprint-test\\n'; } } }\n"
        )
        docker("network", "create", NETWORK)
        try:
            start("backend", "--network-alias", "backend", "--network-alias", "dashboard_dev",
                  "-v", f"{directory}/backend.conf:/tmp/backend.conf:ro", "--entrypoint", "nginx",
                  IMAGE, "-c", "/tmp/backend.conf", "-g", "daemon off;")
            start("anubis", "--network-alias", "anubis",
                  "-e", "BIND=:8923", "-e", "TARGET=http://proxy:8080",
                  "-e", "POLICY_FNAME=/data/cfg/botPolicy.yaml",
                  "-v", f"{ROOT}/anubis/botPolicy.yaml:/data/cfg/botPolicy.yaml:ro",
                  "ghcr.io/techarohq/anubis:v1.25.0")
            proxy = start("proxy", "--network-alias", "proxy",
                          "-p", "127.0.0.1::80", "-p", "127.0.0.1::443",
                          "-e", "PROXY_TARGET=http://backend:8000",
                          "-v", f"{directory}:/etc/nginx/ssl:ro",
                          "-v", f"{directory}:/data/static:ro", IMAGE)
            wait_ready(proxy, 80)
            docker("exec", proxy, "nginx", "-t")

            plain = http.client.HTTPConnection("localhost", port(proxy, 80), timeout=5)
            request(plain, "/plain")
            plain.close()
            for version, label in [(ssl.TLSVersion.TLSv1_2, "12"), (ssl.TLSVersion.TLSv1_3, "13")]:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE  # Ephemeral local test certificate.
                context.minimum_version = context.maximum_version = version
                context.set_alpn_protocols(["http/1.1"])
                connection = http.client.HTTPSConnection("localhost", port(proxy, 443),
                                                         context=context, timeout=5)
                request(connection, f"/tls{label}")
                request(connection, f"/api/reuse{label}")
                connection.close()

            http2 = subprocess.check_output([
                "curl", "--silent", "--show-error", "--fail", "--insecure", "--http2",
                "--noproxy", "*", "--max-time", "10", "--user-agent", USER_AGENT,
                f"https://localhost:{port(proxy, 443)}/http2",
            ], text=True)
            assert http2 == "fingerprint-test\n", http2

            paths = {"/plain", "/tls12", "/api/reuse12", "/tls13", "/api/reuse13", "/http2"}
            rows = records(proxy, paths)
            for row in rows.values():
                check_common(row)
            assert rows["/plain"]["tls_ja4"] in ("", "-"), rows["/plain"]
            assert rows["/http2"]["request"] == "GET /http2 HTTP/2.0", rows["/http2"]
            assert rows["/http2"]["tls_alpn"] == "h2", rows["/http2"]
            assert re.fullmatch(r"t13d\d{4}h2_[0-9a-f]{12}_[0-9a-f]{12}",
                                rows["/http2"]["tls_ja4"]), rows["/http2"]
            for label in ("12", "13"):
                first, second = rows[f"/tls{label}"], rows[f"/api/reuse{label}"]
                assert re.fullmatch(rf"t{label}d\d{{4}}h1_[0-9a-f]{{12}}_[0-9a-f]{{12}}",
                                    first["tls_ja4"]), first
                assert first["tls_protocol"] == f"TLSv1.{label[-1]}", first
                assert first["tls_alpn"] == "http/1.1", first
                for field in ("connection", "tls_ja4", "tcp_ja4t"):
                    assert first[field] == second[field], (field, first, second)
                assert (first["connection_requests"], second["connection_requests"]) == ("1", "2")
                assert first["request_id"] != second["request_id"]
            print(json.dumps(rows, indent=2))

            # The development override must still start without certificates.
            dev = start("dev", "-p", "127.0.0.1::80", "-e", "PROXY_TARGET=http://backend:8000",
                        "-v", f"{ROOT}/proxy/dev/dev.conf.template:/etc/nginx/templates/default.conf.template:ro",
                        IMAGE)
            wait_ready(dev, 80)
            docker("exec", dev, "nginx", "-t")
            connection = http.client.HTTPConnection("localhost", port(dev, 80), timeout=5)
            request(connection, "/dev")
            request(connection, "/api/dev")
            connection.close()
            for row in records(dev, {"/dev", "/api/dev"}).values():
                check_common(row)
                assert row["tls_ja4"] in ("", "-"), row
            print("PASS: HTTP/1.1 and HTTP/2, TLS 1.2/1.3, keepalive, Anubis, static/API routing, "
                  "header spoofing, JSON escaping and certificate-free development config")
        finally:
            for name in reversed(CONTAINERS):
                subprocess.run(["docker", "rm", "-f", "-v", name], check=False, stdout=subprocess.DEVNULL)
            subprocess.run(["docker", "network", "rm", NETWORK], check=False, stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
