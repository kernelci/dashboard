http 'http://localhost:8000/api/tree/android/android-mainline'

# For more specific results, you can use origin parameter or add a git_commit_hash to the route
http 'http://localhost:8000/api/tree/mainline/master/a33b5a08cbbdd7aadff95f40cbb45ab86841679e' origin==microsoft

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 489
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Thu, 26 Jun 2025 11:51:01 GMT
# Expires: Thu, 26 Jun 2025 11:51:01 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "api_url": "/api/tree/mainline/master/a33b5a08cbbdd7aadff95f40cbb45ab86841679e/full?origin=microsoft&git_url=https%3A%2F%2Fgit.kernel.org%2Fpub%2Fscm%2Flinux%2Fkernel%2Fgit%2Ftorvalds%2Flinux.git&git_branch=master",
#     "git_commit_hash": "a33b5a08cbbdd7aadff95f40cbb45ab86841679e",
#     "git_commit_name": "v6.15-rc3-8-ga33b5a08cbbd",
#     "git_repository_branch": "master",
#     "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
#     "origin": "microsoft",
#     "tree_name": "mainline"
# }
