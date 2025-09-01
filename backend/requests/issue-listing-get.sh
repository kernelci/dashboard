http 'http://localhost:8000/api/issue/' interval_in_days==1 filter_issue.culprit==code filter_issue.options==hasIncident starting_date_iso_format=='2025-05-27 13:08:45'

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 242237
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Mon, 01 Sep 2025 17:44:48 GMT
# Expires: Mon, 01 Sep 2025 17:44:48 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "extras": {
#         "maestro:004bf14a80eb6d89368b21c355bb6eaab9497376": {
#             "first_seen": "2025-07-03T11:29:34.479324Z",
#             "git_commit_hash": "b2f3f38d3cb3347db152bc456d94dd77568b2f50",
#             "git_commit_name": "v5.4.295-63-gb2f3f38d3cb33",
#             "git_repository_branch": "linux-5.4.y",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable-rc.git",
#             "issue_version": 1,
#             "tree_name": "stable-rc"
#         },
#         "maestro:0223dc09a1d5442001bff2c9d0addabce3448727": {
#             "first_seen": "2025-07-03T11:29:34.479324Z",
#             "git_commit_hash": "b2f3f38d3cb3347db152bc456d94dd77568b2f50",
#             "git_commit_name": "v5.4.295-63-gb2f3f38d3cb33",
#             "git_repository_branch": "linux-5.4.y",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable-rc.git",
#             "issue_version": 1,
#             "tree_name": "stable-rc"
#         },
#         "maestro:03520bb99ae60b90afb1b08e7d2febc7fc068615": {
#             "first_seen": "2025-08-25T10:35:58.691005Z",
#             "git_commit_hash": "6c68f4c0a147c025ae0b25fab688c7c47964a02f",
#             "git_commit_name": "next-20250825",
#             "git_repository_branch": "master",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git",
#             "issue_version": 1,
#             "tree_name": "next"
#         },
#         ...
#     },
#     "filters": {
#         "categories": [],
#         "culprits": [
#             "code",
#             "harness",
#             "tool"
#         ],
#         "origins": [
#             "_",
#             "maestro",
#             "redhat"
#         ]
#     },
#     "issues": [
#         {
#             "categories": null,
#             "comment": " arch/x86/tools/insn_decoder_test: error: malformed line 5965127: in posttest (arch/x86/tools/Makefile:26) [logspec:kbuild,kbuild.other]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-06-02T10:32:03.310353Z",
#             "id": "redhat:a5eac04d9b50de67ab97fdd463039ec35fae6e5c",
#             "origin": "redhat",
#             "version": 1
#         },
#         {
#             "categories": null,
#             "comment": "[aarch64][coresight_etm4x][kernel 5.19.0] coresight-etm4x: probe of ARMHC500:20 failed with error -17",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-06-26T00:10:34.477963Z",
#             "id": "redhat:issue_1261",
#             "origin": "redhat",
#             "version": 1654694523
#         },
#         {
#             "categories": null,
#             "comment": " arch/x86/tools/insn_decoder_test: error: malformed line 5965213: in posttest (arch/x86/tools/Makefile:26) [logspec:kbuild,kbuild.other]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-06-10T12:45:36.237936Z",
#             "id": "redhat:e785bf812797ba380f48befb2e74cc41afc944e8",
#             "origin": "redhat",
#             "version": 1
#         },
#         ...
#     ]
# }