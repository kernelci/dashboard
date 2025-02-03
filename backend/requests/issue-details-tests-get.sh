# This will get the tests from the issue with the latest version, for a specific version pass ?version=n (n being an integer)
http 'http://localhost:8000/api/issue/maestro:0820fe153b255bf52750bbf1fecb198d8772f5a9/tests'

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 1077
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Tue, 04 Feb 2025 12:22:22 GMT
# Expires: Tue, 04 Feb 2025 12:22:22 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# [
#    {
#       "id":"maestro:674ef566063ce49a02bf7b6d",
#       "status":"FAIL",
#       "duration":null,
#       "path":"boot.nfs",
#       "start_time":"2024-12-03T12:11:18.636000Z",
#       "environment_compatible":[
#          "google,tomato-rev2",
#          "google,tomato",
#          "mediatek,mt8195"
#       ],
#       "tree_name":"net-next",
#       "git_repository_branch":"main"
#    },
#    {
#       "id":"maestro:674fddf9089e99b3f2b506f7",
#       "status":"FAIL",
#       "duration":null,
#       "path":"boot.nfs",
#       "start_time":"2024-12-04T04:43:37.701000Z",
#       "environment_compatible":[
#          "google,tomato-rev2",
#          "google,tomato",
#          "mediatek,mt8195"
#       ],
#       "tree_name":"net-next",
#       "git_repository_branch":"main"
#    },
#    {
#       "id":"maestro:674fd928089e99b3f2b4b523",
#       "status":"FAIL",
#       "duration":null,
#       "path":"boot",
#       "start_time":"2024-12-04T04:23:04.822000Z",
#       "environment_compatible":[
#          "google,tomato-rev2",
#          "google,tomato",
#          "mediatek,mt8195"
#       ],
#       "tree_name":"net-next",
#       "git_repository_branch":"main"
#    },
#    {
#       "id":"maestro:6750002f089e99b3f2b7e106",
#       "status":"FAIL",
#       "duration":null,
#       "path":"boot",
#       "start_time":"2024-12-04T07:09:35.087000Z",
#       "environment_compatible":[
#          "google,tomato-rev2",
#          "google,tomato",
#          "mediatek,mt8195"
#       ],
#       "tree_name":"net-next",
#       "git_repository_branch":"main"
#    }
# ]
