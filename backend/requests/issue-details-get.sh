# shortcut to latest version
http 'http://localhost:8000/api/issue/redhat:issue_2928'                   

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 421
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Thu, 30 Jan 2025 16:49:33 GMT
# Expires: Thu, 30 Jan 2025 16:49:33 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "comment": "rt_ltp: pthread_kill_latency increase threshold based on hardware",
#     "culprit_code": false,
#     "culprit_harness": false,
#     "culprit_tool": true,
#     "field_timestamp": "2024-10-12T22:23:05.071738Z",
#     "id": "redhat:issue_2928",
#     "misc": {},
#     "origin": "redhat",
#     "report_subject": null,
#     "report_url": "https://gitlab.com/redhat/centos-stream/tests/kernel/kernel-tests/-/issues/2024",
#     "version": 1727250638
# }

# Looking for a specific version
http 'http://localhost:8000/api/issue/redhat:issue_2928?version=1726046915' 

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 392
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Thu, 30 Jan 2025 16:49:07 GMT
# Expires: Thu, 30 Jan 2025 16:49:07 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "build_valid": null,
#     "comment": "rt_ltp: subcases will failed sometimes",
#     "culprit_code": null,
#     "culprit_harness": null,
#     "culprit_tool": null,
#     "field_timestamp": "2024-09-23T18:13:05.081721Z",
#     "id": "redhat:issue_2928",
#     "misc": {},
#     "origin": "redhat",
#     "report_subject": null,
#     "report_url": "https://gitlab.com/redhat/centos-stream/tests/kernel/kernel-tests/-/issues/2010",
#     "test_status": null,
#     "version": 1726046915
# }