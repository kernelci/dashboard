http POST http://localhost:8000/api/issue/extras/ \
Content-Type:application/json \
<<< '{
    "issues": [["maestro:7e50acf75c6dfb35b118a15803da9405327eaf55", 1], ["maestro:a5f01e4f2ffb30ed4d5b8cfaabe736cd8608911c", 1]]
}'

# HTTP/1.1 200 OK
# Allow: POST, OPTIONS
# Content-Length: 1100
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Tue, 27 May 2025 16:27:09 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "issues": {
#         "maestro:7e50acf75c6dfb35b118a15803da9405327eaf55": {
#             "first_incident": {
#                 "first_seen": "2025-02-03T19:31:10.399653Z",
#                 "git_commit_hash": "f286757b644c226b6b31779da95a4fa7ab245ef5",
#                 "git_commit_name": "v6.14-rc1-18-gf286757b644c",
#                 "git_repository_branch": "master",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
#                 "tree_name": "mainline"
#             },
#             "versions": {
#                 "1": {
#                     "id": "maestro:7e50acf75c6dfb35b118a15803da9405327eaf55",
#                     "tags": [
#                         "mainline"
#                     ],
#                     "trees": [
#                         {
#                             "git_repository_branch": "master",
#                             "tree_name": "mainline"
#                         }
#                     ],
#                     "version": 1
#                 }
#             }
#         },
#         "maestro:a5f01e4f2ffb30ed4d5b8cfaabe736cd8608911c": {
#             "first_incident": {
#                 "first_seen": "2025-02-03T19:31:10.399653Z",
#                 "git_commit_hash": "f286757b644c226b6b31779da95a4fa7ab245ef5",
#                 "git_commit_name": "v6.14-rc1-18-gf286757b644c",
#                 "git_repository_branch": "master",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
#                 "tree_name": "mainline"
#             },
#             "versions": {
#                 "1": {
#                     "id": "maestro:a5f01e4f2ffb30ed4d5b8cfaabe736cd8608911c",
#                     "tags": [
#                         "mainline"
#                     ],
#                     "trees": [
#                         {
#                             "git_repository_branch": "master",
#                             "tree_name": "mainline"
#                         }
#                     ],
#                     "version": 1
#                 }
#             }
#         }
#     }
# }
