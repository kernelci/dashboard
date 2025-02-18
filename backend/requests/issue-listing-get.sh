http 'localhost:8000/api/issue/?origin=maestro&intervalInDays=1'

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 27282
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Thu, 20 Feb 2025 11:51:56 GMT
# Expires: Thu, 20 Feb 2025 11:51:56 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "extras": {
#         "maestro:031929b615e8ecfed14a89cef2b564108c3aa42c": {
#             "first_seen": "2025-02-17T20:40:01.251254Z",
#             "git_commit_hash": "a1c2670b1577474f7ae60d5dec1d35a053d354f0",
#             "git_commit_name": "v6.1.124-16535-ga1c2670b1577",
#             "git_repository_branch": "chromeos-6.1",
#             "git_repository_url": "https://chromium.googlesource.com/chromiumos/third_party/kernel",
#             "tree_name": "chromiumos"
#         },
#         "maestro:069157741b947b2f589c971be301429c4bb72515": {
#             "first_seen": "2025-02-17T20:40:01.251254Z",
#             "git_commit_hash": "a1c2670b1577474f7ae60d5dec1d35a053d354f0",
#             "git_commit_name": "v6.1.124-16535-ga1c2670b1577",
#             "git_repository_branch": "chromeos-6.1",
#             "git_repository_url": "https://chromium.googlesource.com/chromiumos/third_party/kernel",
#             "tree_name": "chromiumos"
#         },
#         "maestro:11eb365e0d1a4de6c80b036cd2e7a3fe5c276587": {
#             "first_seen": "2024-11-12T10:30:20.456672Z",
#             "git_commit_hash": "d145d3aa80067e115a679d903fba256c3d1f39a1",
#             "git_commit_name": "v5.4.285-53-gd145d3aa8006",
#             "git_repository_branch": "linux-5.4.y",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable-rc.git",
#             "tree_name": "stable-rc"
#         },
#         ...
#     },
#     "issues": [
#         {
#             "comment": " call to undeclared function 'stack_trace_save_tsk'; ISO C99 and later do not support implicit function declarations [-Wimplicit-function-declaration] in kernel/sched/core.o (kernel/sched/core.c) [logspec:kbuild,kbuild.compiler.error]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-02-19T22:51:01.778279Z",
#             "id": "maestro:87244933628a2612f39e6096115454f1e8bb3e1c",
#             "version": 1
#         },
#         {
#             "comment": " implicit declaration of function ‘stack_trace_save_tsk’ [-Werror=implicit-function-declaration] in kernel/sched/core.o (kernel/sched/core.c) [logspec:kbuild,kbuild.compiler.error]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-02-19T23:42:17.982170Z",
#             "id": "maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573",
#             "version": 1
#         },
#         {
#             "comment": " implicit declaration of function 'drm_connector_helper_hpd_irq_event' [-Werror,-Wimplicit-function-declaration] in drivers/gpu/drm/rockchip/cdn-dp-core.o (drivers/gpu/drm/rockchip/cdn-dp-core.c) [logspec:kbuild,kbuild.compiler.error]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-02-20T11:50:02.465668Z",
#             "id": "maestro:3feccbb8dd7c7976251cf4457318fc92c3eb2efb",
#             "version": 1
#         },
#         ...
#     ]
# }
