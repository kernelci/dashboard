# This will get the tests from the issue with the latest version, for a specific version pass ?version=n (n being an integer)
http 'http://localhost:8000/api/issue/maestro:0820fe153b255bf52750bbf1fecb198d8772f5a9/tests'

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 861
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Fri, 31 Jan 2025 13:51:08 GMT
# Expires: Fri, 31 Jan 2025 13:51:08 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# [
#     {
#         "duration": null,
#         "environment_compatible": [
#             "google,tomato-rev2",
#             "google,tomato",
#             "mediatek,mt8195"
#         ],
#         "id": "maestro:674ef566063ce49a02bf7b6d",
#         "path": "boot.nfs",
#         "start_time": "2024-12-03T12:11:18.636000Z",
#         "status": "FAIL"
#     },
#     {
#         "duration": null,
#         "environment_compatible": [
#             "google,tomato-rev2",
#             "google,tomato",
#             "mediatek,mt8195"
#         ],
#         "id": "maestro:674fddf9089e99b3f2b506f7",
#         "path": "boot.nfs",
#         "start_time": "2024-12-04T04:43:37.701000Z",
#         "status": "FAIL"
#     },
#     {
#         "duration": null,
#         "environment_compatible": [
#             "google,tomato-rev2",
#             "google,tomato",
#             "mediatek,mt8195"
#         ],
#         "id": "maestro:674fd928089e99b3f2b4b523",
#         "path": "boot",
#         "start_time": "2024-12-04T04:23:04.822000Z",
#         "status": "FAIL"
#     },
#     {
#         "duration": null,
#         "environment_compatible": [
#             "google,tomato-rev2",
#             "google,tomato",
#             "mediatek,mt8195"
#         ],
#         "id": "maestro:6750002f089e99b3f2b7e106",
#         "path": "boot",
#         "start_time": "2024-12-04T07:09:35.087000Z",
#         "status": "FAIL"
#     }
# ]