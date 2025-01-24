http POST http://localhost:8000/api/hardware/fsl,imx6q-sabrelite/builds \
Content-Type:application/json \
<<< '{
    "origin": "maestro",
    "startTimestampInSeconds": 1733846400,
    "endTimestampInSeconds": 1734105600,
    "selectedCommits": {},
    "filter": {}
}'

# HTTP/1.1 200 OK
# Allow: POST, OPTIONS
# Content-Length: 32644
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Fri, 24 Jan 2025 14:10:11 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "builds": [
#         {
#             "architecture": "arm",
#             "compiler": "gcc-12",
#             "config_name": "multi_v7_defconfig",
#             "config_url": "https://kciapistagingstorage1.file.core.windows.net/production/kbuild-gcc-12-arm-675ae176ca49c97d2997f691/.config?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#             "duration": null,
#             "git_repository_branch": "linux-4.4.y-cip-rt",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/cip/linux-cip.git",
#             "id": "maestro:675ae176ca49c97d2997f691",
#             "issue_id": null,
#             "issue_version": null,
#             "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/kbuild-gcc-12-arm-675ae176ca49c97d2997f691/build.log.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#             "misc": {
#                 "job_context": "gke_android-kernelci-external_us-east4-c_kci-big-us-east4",
#                 "job_id": "kci-675ae176ca49c97d2997f691-kbuild-gcc-12-arm-kogmcp67",
#                 "kernel_type": "zimage",
#                 "platform": "kubernetes",
#                 "runtime": "k8s-all"
#             },
#             "start_time": "2024-12-12T13:13:26.615000Z",
#             "tree_name": "cip",
#             "valid": true
#         },
#         {
#             "architecture": "arm",
#             "compiler": "gcc-12",
#             "config_name": "multi_v7_defconfig",
#             "config_url": "https://kciapistagingstorage1.file.core.windows.net/production/kbuild-gcc-12-arm-675c0fcfca49c97d299e1d37/.config?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#             "duration": null,
#             "git_repository_branch": "master",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/geert/renesas-devel.git",
#             "id": "maestro:675c0fcfca49c97d299e1d37",
#             "issue_id": null,
#             "issue_version": null,
#             "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/kbuild-gcc-12-arm-675c0fcfca49c97d299e1d37/build.log.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#             "misc": {
#                 "job_context": "gke_android-kernelci-external_us-east4-c_kci-big-us-east4",
#                 "job_id": "kci-675c0fcfca49c97d299e1d37-kbuild-gcc-12-arm-sht7a32w",
#                 "kernel_type": "zimage",
#                 "platform": "kubernetes",
#                 "runtime": "k8s-all"
#             },
#             "start_time": "2024-12-13T10:43:27.295000Z",
#             "tree_name": "renesas",
#             "valid": true
#         },
#         ...
