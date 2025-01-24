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
# Content-Length: 125078
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Thu, 23 Jan 2025 16:59:39 GMT
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
#             "id": "maestro:67904d0109f33884b18b9763",
#             "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/baseline-arm64-67904c5509f33884b18b9464/log.txt.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#             "misc": {
#                 "platform": "bcm2711-rpi-4-b"
#             },
#             "path": "boot.dmesg.alert",
#             "start_time": "2025-01-22T01:42:25.618000Z",
#             "status": "PASS"
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
#             "id": "maestro:67904d0109f33884b18b9762",
#             "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/baseline-arm64-67904c5509f33884b18b9464/log.txt.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#             "misc": {
#                 "platform": "bcm2711-rpi-4-b"
#             },
#             "path": "boot.dmesg.emerg",
#             "start_time": "2025-01-22T01:42:25.618000Z",
#             "status": "PASS"
#         },
#         ...
