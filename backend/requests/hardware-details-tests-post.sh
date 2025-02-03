http POST http://localhost:8000/api/hardware/brcm,bcm2711/tests \
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
# Content-Length: 90058
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Tue, 04 Feb 2025 12:36:53 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "tests": [
#         {
#             "architecture": "arm64",
#             "compiler": "gcc-12",
#             "config": "defconfig",
#             "duration": null,
#             "environment_compatible": [
#                 "raspberrypi,4-model-b",
#                 "brcm,bcm2711"
#             ],
#             "git_repository_branch": "master",
#             "id": "maestro:6790844009f33884b18d145d",
#             "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/kselftest-dt-6790844009f33884b18d145d/log.txt.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#             "misc": {
#                 "platform": "bcm2711-rpi-4-b"
#             },
#             "path": "kselftest.dt",
#             "start_time": "2025-01-22T05:38:08.864000Z",
#             "status": "FAIL",
#             "tree_name": "mainline"
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
#             "git_repository_branch": "master",
#             "id": "maestro:6790854709f33884b18d1bd2",
#             "log_url": null,
#             "misc": {
#                 "platform": "bcm2711-rpi-4-b"
#             },
#             "path": "kselftest.dt.dt_test_unprobed_devices_sh_soc_interrupt-controller_40000000",
#             "start_time": "2025-01-22T05:42:31.798000Z",
#             "status": "SKIP",
#             "tree_name": "mainline"
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
#             "git_repository_branch": "master",
#             "id": "maestro:6790854709f33884b18d1bd3",
#             "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/kselftest-dt-6790844009f33884b18d145d/log.txt.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#             "misc": {
#                 "platform": "bcm2711-rpi-4-b"
#             },
#             "path": "kselftest.dt.dt_test_unprobed_devices_sh_soc_i2c_7ef09500",
#             "start_time": "2025-01-22T05:42:31.798000Z",
#             "status": "PASS",
#             "tree_name": "mainline"
#         },
#       ...
