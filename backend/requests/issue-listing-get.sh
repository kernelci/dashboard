http 'localhost:8000/api/issue/?intervalInDays=1&filter_issue.culprit=code'

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 46881
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Tue, 27 May 2025 13:08:45 GMT
# Expires: Tue, 27 May 2025 13:08:45 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "extras": {
#         "maestro:0d3cbb147d638deb60ed276f06896eef38fcf2a0": {
#             "first_seen": "2025-04-16T17:36:54.942971Z",
#             "git_commit_hash": "c62f4b82d57155f35befb5c8bbae176614b87623",
#             "git_commit_name": "v6.15-rc2-48-gc62f4b82d5715",
#             "git_repository_branch": "master",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
#             "tree_name": "mainline"
#         },
#         "maestro:3e57cb725c9d3e8acaf42a61e15b3c07c0e4ca60": {
#             "first_seen": "2025-04-16T23:27:17.553063Z",
#             "git_commit_hash": "c1336865c4c90fcc649df0435a7c86c30030a723",
#             "git_commit_name": "v6.15-rc2-55-gc1336865c4c90",
#             "git_repository_branch": "master",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
#             "tree_name": "mainline"
#         },
#         "maestro:441ce4ab6a1945cc42c0233e47d2f95614fb58a5": {
#             "first_seen": "2025-04-16T17:55:11.571263Z",
#             "git_commit_hash": "c62f4b82d57155f35befb5c8bbae176614b87623",
#             "git_commit_name": "v6.15-rc2-48-gc62f4b82d5715",
#             "git_repository_branch": "master",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
#             "tree_name": "mainline"
#         },
#         ...
#     },
#     "issues": [
#         {
#             "categories": null,
#             "comment": " implicit declaration of function ‘lru_raw_gen_from_flags’ [-Werror=implicit-function-declaration] in mm/vmscan.o (mm/vmscan.c) [logspec:kbuild,kbuild.compiler.error]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T13:41:21.131199Z",
#             "id": "maestro:e5d19aafa06d4af009e6569b4a0b03b690d9e29a",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "categories": null,
#             "comment": " error: relocation R_386_32 cannot be used against local symbol; recompile with -fPIC in arch/x86/boot/compressed/vmlinux (arch/x86/boot/compressed/Makefile:124) [logspec:kbuild,kbuild.compiler.linker_error]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T14:03:28.234078Z",
#             "id": "maestro:ab940af48ff006abcf41620daba4d0fe959116f9",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "categories": null,
#             "comment": " ‘input’ is a pointer; did you mean to use ‘->’? in drivers/gpu/drm/amd/amdgpu/../display/dc/calcs/dcn_calcs.o (drivers/gpu/drm/amd/amdgpu/../display/dc/calcs/dcn_calcs.c) [logspec:kbuild,kbuild.compiler.error]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T14:26:31.608536Z",
#             "id": "maestro:bd048bdc8156ad24e3a5903c41c0424edc532371",
#             "origin": "maestro",
#             "version": 1
#         }
#     ]
# }