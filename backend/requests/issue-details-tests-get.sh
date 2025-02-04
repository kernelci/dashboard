# This will get the tests from the issue with the latest version, for a specific version pass ?version=n (n being an integer)
http 'http://localhost:8000/api/issue/maestro:0820fe153b255bf52750bbf1fecb198d8772f5a9/tests'

HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 1589
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Tue, 04 Feb 2025 13:12:08 GMT
# Expires: Tue, 04 Feb 2025 13:12:08 GMT
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
#         "git_repository_branch": "main",
#         "id": "maestro:674ef566063ce49a02bf7b6d",
#         "environment_misc": {
#             "job_id": "16727012",
#             "job_url": "https://lava.collabora.dev/scheduler/job/16727012",
#             "platform": "mt8195-cherry-tomato-r2"
#         },
#         "path": "boot.nfs",
#         "start_time": "2024-12-03T12:11:18.636000Z",
#         "status": "FAIL",
#         "tree_name": "net-next"
#     },
#     {
#         "duration": null,
#         "environment_compatible": [
#             "google,tomato-rev2",
#             "google,tomato",
#             "mediatek,mt8195"
#         ],
#         "git_repository_branch": "main",
#         "id": "maestro:674fddf9089e99b3f2b506f7",
#         "environment_misc": {
#             "job_id": "16759244",
#             "job_url": "https://lava.collabora.dev/scheduler/job/16759244",
#             "platform": "mt8195-cherry-tomato-r2"
#         },
#         "path": "boot.nfs",
#         "start_time": "2024-12-04T04:43:37.701000Z",
#         "status": "FAIL",
#         "tree_name": "net-next"
#     },
#     {
#         "duration": null,
#         "environment_compatible": [
#             "google,tomato-rev2",
#             "google,tomato",
#             "mediatek,mt8195"
#         ],
#         "git_repository_branch": "main",
#         "id": "maestro:674fd928089e99b3f2b4b523",
#         "environment_misc": {
#             "job_id": "16757607",
#             "job_url": "https://lava.collabora.dev/scheduler/job/16757607",
#             "platform": "mt8195-cherry-tomato-r2"
#         },
#         "path": "boot",
#         "start_time": "2024-12-04T04:23:04.822000Z",
#         "status": "FAIL",
#         "tree_name": "net-next"
#     },
#     {
#         "duration": null,
#         "environment_compatible": [
#             "google,tomato-rev2",
#             "google,tomato",
#             "mediatek,mt8195"
#         ],
#         "git_repository_branch": "main",
#         "id": "maestro:6750002f089e99b3f2b7e106",
#         "environment_misc": {
#             "job_id": "16770923",
#             "job_url": "https://lava.collabora.dev/scheduler/job/16770923",
#             "platform": "mt8195-cherry-tomato-r2"
#         },
#         "path": "boot",
#         "start_time": "2024-12-04T07:09:35.087000Z",
#         "status": "FAIL",
#         "tree_name": "net-next"
#     }
# ]