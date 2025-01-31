# This will get the builds from the issue with the latest version
http http://localhost:8000/api/issue/maestro:bba672c389cd8e575694e468d87a80b1b4074241/builds

# To get the builds from the issue with the specific version use this as an example:
# http http://localhost:8000/api/issue/maestro:bba672c389cd8e575694e468d87a80b1b4074241/builds?version=0

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 493
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Fri, 31 Jan 2025 13:11:33 GMT
# Expires: Fri, 31 Jan 2025 13:11:33 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# [
#     {
#         "architecture": "riscv",
#         "compiler": "clang-17",
#         "config_name": "defconfig+allnoconfig",
#         "duration": null,
#         "id": "maestro:67952a5e09f33884b1941e14",
#         "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/kbuild-clang-17-riscv-android-defconfig-67952a5e09f33884b1941e14/build.log.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#         "start_time": "2025-01-25T18:15:58.287000Z",
#         "valid": false
#     }
# ]