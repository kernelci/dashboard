# If you want to see headers, add -p H to the http call:
# http -p H 'http://localhost:8000/api/tree/' origin==0dayci

# If you want to provide another limit to query:
http 'http://localhost:8000/api/tree/' origin==maestro intervalInDays==4

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 25325
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Thu, 03 Apr 2025 16:44:20 GMT
# Expires: Thu, 03 Apr 2025 16:44:20 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# [
#     {
#         "boot_status": {
#             "done": 0,
#             "error": 0,
#             "fail": 0,
#             "miss": 4,
#             "null": 0,
#             "pass": 5,
#             "skip": 0
#         },
#         "build_status": {
#             "DONE": 0,
#             "ERROR": 0,
#             "FAIL": 0,
#             "MISS": 0,
#             "NULL": 0,
#             "PASS": 30,
#             "SKIP": 0
#         },
#         "git_commit_hash": "7c1a6949984d3a50c659ee423adf5a7efc61aab2",
#         "git_commit_name": "android14-6.1.129_r00-331-g7c1a6949984d",
#         "git_commit_tags": [],
#         "git_repository_branch": "android14-6.1-lts",
#         "git_repository_url": "https://android.googlesource.com/kernel/common",
#         "id": "maestro:67ea971ddd0dd865e918efd5",
#         "origin_builds_finish_time": null,
#         "origin_tests_finish_time": null,
#         "start_time": "2025-03-31T13:22:37.444000Z",
#         "test_status": {
#             "done": 0,
#             "error": 0,
#             "fail": 0,
#             "miss": 0,
#             "null": 0,
#             "pass": 4,
#             "skip": 0
#         },
#         "tree_name": "android"
#     },
#     {
#         "boot_status": {
#             "done": 0,
#             "error": 0,
#             "fail": 1,
#             "miss": 20,
#             "null": 0,
#             "pass": 40,
#             "skip": 0
#         },
#         "build_status": {
#             "DONE": 0,
#             "ERROR": 0,
#             "FAIL": 0,
#             "MISS": 0,
#             "NULL": 0,
#             "PASS": 13,
#             "SKIP": 0
#         },
#         "git_commit_hash": "47d25ec1239844c5ae3f7b60527c20f225ff016a",
#         "git_commit_name": "net-next-6.15-4096-g47d25ec123984",
#         "git_commit_tags": [],
#         "git_repository_branch": "net-next-hw-2025-03-31--00-00",
#         "git_repository_url": "https://github.com/linux-netdev/testing.git",
#         "id": "maestro:67e9e1ac67593f2aa04084e5",
#         "origin_builds_finish_time": null,
#         "origin_tests_finish_time": null,
#         "start_time": "2025-03-31T00:28:28.486000Z",
#         "test_status": {
#             "done": 0,
#             "error": 1,
#             "fail": 9,
#             "miss": 0,
#             "null": 1,
#             "pass": 749,
#             "skip": 436
#         },
#         "tree_name": "netdev-testing"
#     },
#     ...
