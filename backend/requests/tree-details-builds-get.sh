http 'http://localhost:8000/api/tree/b7bfaa761d760e72a969d116517eaa12e404c262/builds' git_branch==for-kernelci git_url==https://git.kernel.org/pub/scm/linux/kernel/git/broonie/misc.git origin==maestro

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Content-Length: 8706
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Fri, 24 Jan 2025 14:11:20 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "builds": [
#         {
#             "architecture": "arm64",
#             "compiler": "gcc-12",
#             "config_name": "defconfig",
#             "config_url": "https://kciapistagingstorage1.file.core.windows.net/early-access/kbuild-gcc-12-arm64-chromebook-6686b975f686ead9f9232f23/.config?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2024-10-17T19:19:12Z&st=2023-10-17T11:19:12Z&spr=https&sig=sLmFlvZHXRrZsSGubsDUIvTiv%2BtzgDq6vALfkrtWnv8%3D",
#             "duration": null,
#             "git_repository_branch": "for-kernelci",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/broonie/misc.git",
#             "id": "maestro:6686b975f686ead9f9232f23",
#             "log_url": "https://kciapistagingstorage1.file.core.windows.net/early-access/kbuild-gcc-12-arm64-chromebook-6686b975f686ead9f9232f23/build.log.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2024-10-17T19:19:12Z&st=2023-10-17T11:19:12Z&spr=https&sig=sLmFlvZHXRrZsSGubsDUIvTiv%2BtzgDq6vALfkrtWnv8%3D",
#             "misc": {
#                 "platform": "kubernetes"
#             },
#             "start_time": "2024-07-04T15:02:13.615000Z",
#             "valid": true
#         },
#         {
#             "architecture": "Unknown",
#             "compiler": "Unknown",
#             "config_name": "Unknown",
#             "config_url": null,
#             "duration": null,
#             "git_repository_branch": "for-kernelci",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/broonie/misc.git",
#             "id": "maestro:6686b976f686ead9f9232f28",
#             "log_url": null,
#             "misc": {
#                 "platform": "kubernetes"
#             },
#             "start_time": "2024-07-04T15:02:14.562000Z",
#             "valid": false
#         },
#         ...
