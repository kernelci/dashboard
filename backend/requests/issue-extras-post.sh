http POST http://localhost:8000/api/issue/extras/ \
Content-Type:application/json \
<<< '{
    "issues": [["maestro:7e50acf75c6dfb35b118a15803da9405327eaf55", 1], ["maestro:a5f01e4f2ffb30ed4d5b8cfaabe736cd8608911c", 1]]
}'

# HTTP/1.1 200 OK
# Allow: POST, OPTIONS
# Content-Length: 528
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Mon, 10 Feb 2025 17:00:36 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "issues": {
#         "maestro:7e50acf75c6dfb35b118a15803da9405327eaf55": {
#             "1": {
#                 "first_seen": "2025-02-03T19:31:10.399653Z",
#                 "id": "maestro:7e50acf75c6dfb35b118a15803da9405327eaf55",
#                 "tags": [
#                     "mainline"
#                 ],
#                 "trees": [
#                     {
#                         "git_repository_branch": "master",
#                         "tree_name": "mainline"
#                     }
#                 ],
#                 "version": 1
#             }
#         },
#         "maestro:a5f01e4f2ffb30ed4d5b8cfaabe736cd8608911c": {
#             "1": {
#                 "first_seen": "2025-02-03T19:31:10.399653Z",
#                 "id": "maestro:a5f01e4f2ffb30ed4d5b8cfaabe736cd8608911c",
#                 "tags": [
#                     "mainline"
#                 ],
#                 "trees": [
#                     {
#                         "git_repository_branch": "master",
#                         "tree_name": "mainline"
#                     }
#                 ],
#                 "version": 1
#             }
#         }
#     }
# }
