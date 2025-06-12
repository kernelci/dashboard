# If you want to see headers, add -p H to the http call:
# http -p H 'http://localhost:8000/api/tree/' origin==maestro

# If you want to provide another limit to query:
http 'http://localhost:8000/api/tree-fast/' origin==maestro interval_in_days==4

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 16855
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Thu, 03 Apr 2025 16:45:54 GMT
# Expires: Thu, 03 Apr 2025 16:45:54 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# [
#     {
#         "git_commit_hash": "49807ed87851916ef655f72e9562f96355183090",
#         "git_commit_name": "amlogic-arm64-dt-for-v6.15-v2-22-g49807ed878519",
#         "git_commit_tags": [],
#         "git_repository_branch": "for-next",
#         "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/amlogic/linux.git",
#         "id": "maestro:67ee57c9dd0dd865e91fc692",
#         "origin_builds_finish_time": null,
#         "origin_tests_finish_time": null,
#         "patchset_hash": "",
#         "start_time": "2025-04-03T09:41:29.389000Z",
#         "tree_name": "amlogic"
#     },
#     {
#         "git_commit_hash": "3e6e324f5b472ff8460615f1403f380e05cf2b67",
#         "git_commit_name": "android14-6.1.129_r00-54-g3e6e324f5b472",
#         "git_commit_tags": [],
#         "git_repository_branch": "android14-6.1",
#         "git_repository_url": "https://android.googlesource.com/kernel/common",
#         "id": "maestro:67ebdbe1dd0dd865e91b016c",
#         "origin_builds_finish_time": null,
#         "origin_tests_finish_time": null,
#         "patchset_hash": "",
#         "start_time": "2025-04-01T12:28:17.537000Z",
#         "tree_name": "android"
#     },
#     ...
