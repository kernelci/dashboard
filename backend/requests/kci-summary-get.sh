http "http://localhost:8000/api/kci-summary/" git_branch==for-kernelci git_url==https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git origin==maestro

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Content-Length: 3677
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Wed, 02 Jul 2025 17:57:35 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "boot_status_summary": {
#         "done_count": 0,
#         "error_count": 0,
#         "fail_count": 0,
#         "miss_count": 13,
#         "null_count": 0,
#         "pass_count": 9,
#         "skip_count": 0
#     },
#     "build_status_summary": {
#         "DONE": 0,
#         "ERROR": 0,
#         "FAIL": 0,
#         "MISS": 0,
#         "NULL": 0,
#         "PASS": 9,
#         "SKIP": 0
#     },
#     "checkout_start_time": "2025-07-01T15:08:26.610000Z",
#     "commit_hash": "3c795c3404e82c4db5c69317847dc5bbafbb368b",
#     "dashboard_url": "https://d.kernelci.org/tree/arm64/for-kernelci/3c795c3404e82c4db5c69317847dc5bbafbb368b?o=maestro",
#     "fixed_regressions": {},
#     "git_branch": "for-kernelci",
#     "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git",
#     "origin": "maestro",
#     "possible_regressions": {},
#     "test_status_summary": {
#         "done_count": 0,
#         "error_count": 0,
#         "fail_count": 0,
#         "miss_count": 0,
#         "null_count": 62,
#         "pass_count": 592,
#         "skip_count": 0
#     },
#     "unstable_tests": {
#         "bcm2711-rpi-4-b": {
#             "defconfig+lab-setup+kselftest": {
#                 "boot": [
#                     {
#                         "id": "maestro:686413d35c2cf25042f65ec8",
#                         "start_time": "2025-07-01T16:58:59.086000Z",
#                         "status": "MISS"
#                     },
#                     {
#                         "id": "maestro:686413cf5c2cf25042f65ead",
#                         "start_time": "2025-07-01T16:58:55.436000Z",
#                         "status": "PASS"
#                     },
#                     {
#                         "id": "maestro:6862e6f15c2cf25042f38ba1",
#                         "start_time": "2025-06-30T19:35:13.117000Z",
#                         "status": "PASS"
#                     },
#                     {
#                         "id": "maestro:6862e6ed5c2cf25042f38b85",
#                         "start_time": "2025-06-30T19:35:09.018000Z",
#                         "status": "PASS"
#                     }
#                 ]
#             }
#         },
#         ...
#     }
# }