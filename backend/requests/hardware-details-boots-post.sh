http POST http://localhost:8000/api/hardware/brcm,bcm2711/boots \
Content-Type:application/json \
<<< '{
    "origin":"maestro",
    "startTimestampInSeconds":1737487800,
    "endTimestampInSeconds":1737574200,
    "selectedCommits":{},
    "filter":{}
}'

# HTTP/1.1 200 OK
# Allow: POST, OPTIONS
# Content-Length: 137950
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Tue, 04 Feb 2025 12:35:29 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "boots": [
#         {
#             "architecture": "arm64",
#             "compiler": "gcc-12",
#             "config": "defconfig",
#             "duration": null,
#             "environment_compatible": [
#                 "raspberrypi,4-model-b",
#                 "brcm,bcm2711"
#             ],
#             "git_repository_branch": "pending-fixes",
#             "id": "maestro:679045cf09f33884b18b7c2c",
#             "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/baseline-arm64-679045cf09f33884b18b7c2c/log.txt.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#             "misc": {
#                 "platform": "bcm2711-rpi-4-b"
#             },
#             "path": "boot",
#             "start_time": "2025-01-22T01:11:43.067000Z",
#             "status": "PASS",
#             "tree_name": "next"
#         },
#         {
#             "architecture": "arm64",
#             "compiler": "gcc-12",
#             "config": "defconfig",
#             "duration": null,
#             "environment_compatible": [
#                 "raspberrypi,4-model-b",
#                 "brcm,bcm2711"
#             ],
#             "git_repository_branch": "pending-fixes",
#             "id": "maestro:6790466509f33884b18b8039",
#             "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/baseline-arm64-679045cf09f33884b18b7c2c/log.txt.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#             "misc": {
#                 "platform": "bcm2711-rpi-4-b"
#             },
#             "path": "boot.dmesg",
#             "start_time": "2025-01-22T01:14:13.810000Z",
#             "status": "PASS",
#             "tree_name": "next"
#         },
#         {
#             "architecture": "arm64",
#             "compiler": "gcc-12",
#             "config": "defconfig",
#             "duration": null,
#             "environment_compatible": [
#                 "raspberrypi,4-model-b",
#                 "brcm,bcm2711"
#             ],
#             "git_repository_branch": "pending-fixes",
#             "id": "maestro:6790466509f33884b18b803a",
#             "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/baseline-arm64-679045cf09f33884b18b7c2c/log.txt.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#             "misc": {
#                 "platform": "bcm2711-rpi-4-b"
#             },
#             "path": "boot.dmesg.emerg",
#             "start_time": "2025-01-22T01:14:13.810000Z",
#             "status": "PASS",
#             "tree_name": "next"
#         },
#         ...
