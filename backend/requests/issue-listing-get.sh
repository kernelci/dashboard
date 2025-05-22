http 'localhost:8000/api/issue/?intervalInDays=1&filter_issue.culprit=code'

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 8648
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Mon, 26 May 2025 13:35:53 GMT
# Expires: Mon, 26 May 2025 13:35:53 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "extras": {
#         "maestro:0d3cbb147d638deb60ed276f06896eef38fcf2a0": {
#             "first_seen": "2025-04-16T17:36:54.942971Z",
#             "git_commit_hash": "c62f4b82d57155f35befb5c8bbae176614b87623",
#             "git_commit_name": "v6.15-rc2-48-gc62f4b82d5715",
#             "git_repository_branch": "master",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
#             "tree_name": "mainline"
#         },
#         "maestro:1ec0ababeee988e6d6392eedfbe6a035ed2dfd6d": {
#             "first_seen": "2025-05-26T09:19:39.257435Z",
#             "git_commit_hash": "3be1a7a31fbda82f3604b6c31e4f390110de1b46",
#             "git_commit_name": "next-20250526",
#             "git_repository_branch": "master",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git",
#             "tree_name": "next"
#         },
#         "maestro:3e57cb725c9d3e8acaf42a61e15b3c07c0e4ca60": {
#             "first_seen": "2025-04-16T23:27:17.553063Z",
#             "git_commit_hash": "c1336865c4c90fcc649df0435a7c86c30030a723",
#             "git_commit_name": "v6.15-rc2-55-gc1336865c4c90",
#             "git_repository_branch": "master",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
#             "tree_name": "mainline"
#         },
#         "maestro:441ce4ab6a1945cc42c0233e47d2f95614fb58a5": {
#             "first_seen": "2025-04-16T17:55:11.571263Z",
#             "git_commit_hash": "c62f4b82d57155f35befb5c8bbae176614b87623",
#             "git_commit_name": "v6.15-rc2-48-gc62f4b82d5715",
#             "git_repository_branch": "master",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
#             "tree_name": "mainline"
#         },
#         "maestro:66a7d9a1dc10e7ffafe798f2bca0a593dbd23eaf": {
#             "first_seen": "2025-04-16T07:47:16.133431Z",
#             "git_commit_hash": "f660850bc246fef15ba78c81f686860324396628",
#             "git_commit_name": "next-20250416",
#             "git_repository_branch": "master",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git",
#             "tree_name": "next"
#         },
#         "maestro:721516cb40a17ba5aaddc2e6e410d3eec5c49fc6": {
#             "first_seen": "2025-01-21T00:44:16.494094Z",
#             "git_commit_hash": "d73a4602e973e9e922f00c537a4643907a547ade",
#             "git_commit_name": "pm-6.13-rc8-1598-gd73a4602e973",
#             "git_repository_branch": "main",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net-next.git",
#             "tree_name": "net-next"
#         },
#         "maestro:7c81c13ebf1e0b7efda9125b328de6a02b01a813": {
#             "first_seen": "2025-02-18T22:36:01.533999Z",
#             "git_commit_hash": "33aeeccfa4c78060c7135794ff33b4df378e32d4",
#             "git_commit_name": "v6.6.70-6982-g33aeeccfa4c78",
#             "git_repository_branch": "chromeos-6.6",
#             "git_repository_url": "https://chromium.googlesource.com/chromiumos/third_party/kernel",
#             "tree_name": "chromiumos"
#         },
#         "maestro:ab940af48ff006abcf41620daba4d0fe959116f9": {
#             "first_seen": "2024-11-21T03:28:01.079277Z",
#             "git_commit_hash": "fd0bf47f6276a13190b907eb46f5707526494dcc",
#             "git_commit_name": "ASB-2024-11-05_11-5.4-14-gfd0bf47f6276",
#             "git_repository_branch": "android11-5.4",
#             "git_repository_url": "https://android.googlesource.com/kernel/common",
#             "tree_name": "android"
#         },
#         "maestro:bd048bdc8156ad24e3a5903c41c0424edc532371": {
#             "first_seen": "2025-05-13T10:07:42.224250Z",
#             "git_commit_hash": "9610ed5f00dc3dc63655a10cbabf7c6429c2886e",
#             "git_commit_name": "ASB-2025-05-05_13-5.10-2-g9610ed5f00dc",
#             "git_repository_branch": "android13-5.10",
#             "git_repository_url": "https://android.googlesource.com/kernel/common",
#             "tree_name": "android"
#         },
#         "maestro:d9c9973aa170e504ca712710292ace4050b7a4de": {
#             "first_seen": "2025-03-14T01:37:01.590750Z",
#             "git_commit_hash": "8ba2d538033ce80fc41ddd355fde50424ea10c66",
#             "git_commit_name": "v5.10.234-26066-g8ba2d538033ce",
#             "git_repository_branch": "chromeos-5.10",
#             "git_repository_url": "https://chromium.googlesource.com/chromiumos/third_party/kernel",
#             "tree_name": "chromiumos"
#         },
#         "maestro:da694c56147298d223ee432ad8d6a8ee311b773a": {
#             "first_seen": "2025-01-21T00:22:10.827866Z",
#             "git_commit_hash": "d73a4602e973e9e922f00c537a4643907a547ade",
#             "git_commit_name": "pm-6.13-rc8-1598-gd73a4602e973",
#             "git_repository_branch": "main",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net-next.git",
#             "tree_name": "net-next"
#         },
#         "maestro:e602fca280d85d8e603f7c0aff68363bb0cd7993": {
#             "first_seen": "2025-01-21T00:24:05.705873Z",
#             "git_commit_hash": "d73a4602e973e9e922f00c537a4643907a547ade",
#             "git_commit_name": "pm-6.13-rc8-1598-gd73a4602e973",
#             "git_repository_branch": "main",
#             "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net-next.git",
#             "tree_name": "net-next"
#         }
#     },
#     "issues": [
#         {
#             "comment": " WARNING at mm/early_ioremap.c:90 check_early_ioremap_leak+0x39/0x50 [logspec:generic_linux_boot,linux.kernel.warning]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T01:33:59.673657Z",
#             "id": "maestro:441ce4ab6a1945cc42c0233e47d2f95614fb58a5",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "comment": " WARNING at mm/early_ioremap.c:90 check_early_ioremap_leak+0x38/0x50 [logspec:generic_linux_boot,linux.kernel.warning]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T03:20:21.745175Z",
#             "id": "maestro:0d3cbb147d638deb60ed276f06896eef38fcf2a0",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "comment": " in vmlinux (Makefile:1215) [logspec:kbuild,kbuild.other]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T05:05:33.073167Z",
#             "id": "maestro:d9c9973aa170e504ca712710292ace4050b7a4de",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "comment": " incompatible pointer to integer conversion returning 'void *' from a function with result type 'int' [-Wint-conversion] in drivers/media/platform/camx/cam_sensor_module/cam_eeprom/cam_eeprom_dev.o (drivers/media/platform/camx/cam_sensor_module/cam_eeprom/cam_eeprom_dev.c) [logspec:kbuild,kbuild.compiler.error]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T05:13:24.843369Z",
#             "id": "maestro:7c81c13ebf1e0b7efda9125b328de6a02b01a813",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "comment": " ‘SOCK_COREDUMP’ undeclared (first use in this function); did you mean ‘SOCK_RDM’? in net/unix/af_unix.o (net/unix/af_unix.c) [logspec:kbuild,kbuild.compiler.error]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T09:43:10.311911Z",
#             "id": "maestro:1ec0ababeee988e6d6392eedfbe6a035ed2dfd6d",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "comment": " WARNING at mm/early_ioremap.c:90 check_early_ioremap_leak+0x48/0x68 [logspec:generic_linux_boot,linux.kernel.warning]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T10:49:58.828888Z",
#             "id": "maestro:66a7d9a1dc10e7ffafe798f2bca0a593dbd23eaf",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "comment": " WARNING: Unclean boot. Reached prompt but marked as failed. [logspec:generic_linux_boot,maestro.linux.kernel.boot]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T10:49:58.828888Z",
#             "id": "maestro:721516cb40a17ba5aaddc2e6e410d3eec5c49fc6",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "comment": " error: relocation R_386_32 cannot be used against local symbol; recompile with -fPIC in arch/x86/boot/compressed/vmlinux (arch/x86/boot/compressed/Makefile:124) [logspec:kbuild,kbuild.compiler.linker_error]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T11:17:18.919021Z",
#             "id": "maestro:ab940af48ff006abcf41620daba4d0fe959116f9",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "comment": " ‘input’ is a pointer; did you mean to use ‘->’? in drivers/gpu/drm/amd/amdgpu/../display/dc/calcs/dcn_calcs.o (drivers/gpu/drm/amd/amdgpu/../display/dc/calcs/dcn_calcs.c) [logspec:kbuild,kbuild.compiler.error]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T12:11:59.483340Z",
#             "id": "maestro:bd048bdc8156ad24e3a5903c41c0424edc532371",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "comment": " stack frame size (2336) exceeds limit (2048) in 'curve25519_generic' [-Werror,-Wframe-larger-than] in lib/crypto/curve25519-hacl64.o (lib/crypto/curve25519-hacl64.c) [logspec:kbuild,kbuild.compiler.error]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T12:56:17.456762Z",
#             "id": "maestro:3e57cb725c9d3e8acaf42a61e15b3c07c0e4ca60",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "comment": " Bootloader did not finish or kernel did not start. [logspec:generic_linux_boot,maestro.linux.kernel.boot]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T13:00:50.659846Z",
#             "id": "maestro:e602fca280d85d8e603f7c0aff68363bb0cd7993",
#             "origin": "maestro",
#             "version": 1
#         },
#         {
#             "comment": " Bootloader did not finish or kernel did not start. [logspec:generic_linux_boot,maestro.linux.kernel.boot]",
#             "culprit_code": true,
#             "culprit_harness": false,
#             "culprit_tool": false,
#             "field_timestamp": "2025-05-26T13:18:38.434375Z",
#             "id": "maestro:da694c56147298d223ee432ad8d6a8ee311b773a",
#             "origin": "maestro",
#             "version": 1
#         }
#     ]
# }