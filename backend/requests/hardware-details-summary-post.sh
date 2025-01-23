http POST http://localhost:8000/api/hardware/google,juniper/summary \
Content-Type:application/json \
<<< '{
    "origin":"maestro",
    "startTimestampInSeconds":1737046800,
    "endTimestampInSeconds":1737478800,
    "selectedCommits":{},
    "filter":{}
}'

# HTTP/1.1 200 OK
# Allow: POST, OPTIONS
# Content-Length: 9063
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Tue, 21 Jan 2025 16:48:47 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "summary": {
#         "architectures": [
#             "arm64"
#         ],
#         "boots": {
#             "architectures": [
#                 {
#                     "arch": "arm64",
#                     "compiler": "gcc-12",
#                     "status": {
#                         "ERROR": 0,
#                         "FAIL": 1,
#                         "MISS": 0,
#                         "NULL": 6,
#                         "PASS": 202,
#                         "SKIP": 0
#                     }
#                 }
#             ],
#             "configs": {
#                 "cros://chromeos-6.6/arm64/chromiumos-mediatek.flavour.config": {
#                     "ERROR": 0,
#                     "FAIL": 0,
#                     "MISS": 0,
#                     "NULL": 0,
#                     "PASS": 75,
#                     "SKIP": 0
#                 },
#                 "defconfig": {
#                     "ERROR": 0,
#                     "FAIL": 1,
#                     "MISS": 0,
#                     "NULL": 6,
#                     "PASS": 127,
#                     "SKIP": 0
#                 }
#             },
#             "environment_compatible": null,
#             "environment_misc": null,
#             "fail_reasons": {},
#             "failed_platforms": [],
#             "issues": [
#                 {
#                     "comment": "[logspec:generic_linux_boot] linux.kernel.ubsan shift-out-of-bounds: shift exponent -1 is negative",
#                     "id": "maestro:b91eba41d9d0281c086ee574a82bdee035760751",
#                     "incidents_info": {
#                         "incidentsCount": 1
#                     },
#                     "report_url": null,
#                     "version": "0"
#                 }
#             ],
#             "platforms": {
#                 "mt8183-kukui-jacuzzi-juniper-sku16": {
#                     "ERROR": 0,
#                     "FAIL": 1,
#                     "MISS": 0,
#                     "NULL": 6,
#                     "PASS": 202,
#                     "SKIP": 0
#                 }
#             },
#             "status": {
#                 "ERROR": 0,
#                 "FAIL": 1,
#                 "MISS": 0,
#                 "NULL": 6,
#                 "PASS": 202,
#                 "SKIP": 0
#             },
#             "unknown_issues": 0
#         },
#         "builds": {
#             "architectures": {
#                 "arm64": {
#                     "compilers": [
#                         "gcc-12"
#                     ],
#                     "invalid": 0,
#                     "null": 0,
#                     "valid": 39
#                 }
#             },
#             "configs": {
#                 "cros://chromeos-6.6/arm64/chromiumos-mediatek.flavour.config": {
#                     "invalid": 0,
#                     "null": 0,
#                     "valid": 12
#                 },
#                 "defconfig": {
#                     "invalid": 0,
#                     "null": 0,
#                     "valid": 27
#                 }
#             },
#             "issues": [],
#             "status": {
#                 "invalid": 0,
#                 "null": 0,
#                 "valid": 39
#             },
#             "unknown_issues": 0
#         },
#         "compatibles": [
#             "google,juniper",
#             "google,juniper-sku16",
#             "mediatek,mt8183"
#         ],
#         "compilers": [
#             "gcc-12"
#         ],
#         "configs": [
#             "cros://chromeos-6.6/arm64/chromiumos-mediatek.flavour.config",
#             "defconfig"
#         ],
#         "tests": {
#             "architectures": [
#                 {
#                     "arch": "arm64",
#                     "compiler": "gcc-12",
#                     "status": {
#                         "ERROR": 4,
#                         "FAIL": 2169,
#                         "MISS": 9,
#                         "NULL": 8,
#                         "PASS": 2789,
#                         "SKIP": 352
#                     }
#                 }
#             ],
#             "configs": {
#                 "cros://chromeos-6.6/arm64/chromiumos-mediatek.flavour.config": {
#                     "ERROR": 2,
#                     "FAIL": 188,
#                     "MISS": 5,
#                     "NULL": 2,
#                     "PASS": 239,
#                     "SKIP": 0
#                 },
#                 "defconfig": {
#                     "ERROR": 2,
#                     "FAIL": 1981,
#                     "MISS": 4,
#                     "NULL": 6,
#                     "PASS": 2550,
#                     "SKIP": 352
#                 }
#             },
#             "environment_compatible": null,
#             "environment_misc": null,
#             "fail_reasons": {},
#             "failed_platforms": [],
#             "issues": [],
#             "platforms": {
#                 "mt8183-kukui-jacuzzi-juniper-sku16": {
#                     "ERROR": 4,
#                     "FAIL": 2169,
#                     "MISS": 9,
#                     "NULL": 8,
#                     "PASS": 2789,
#                     "SKIP": 352
#                 }
#             },
#             "status": {
#                 "ERROR": 4,
#                 "FAIL": 2169,
#                 "MISS": 9,
#                 "NULL": 8,
#                 "PASS": 2789,
#                 "SKIP": 352
#             },
#             "unknown_issues": 2169
#         },
#         "trees": [
#             {
#                 "git_repository_branch": "for-kernelci",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git",
#                 "head_git_commit_hash": "1950a0af2d55e0ecbcc574927bad495bfaddcec0",
#                 "head_git_commit_name": "v6.13-rc7-71-g1950a0af2d55e",
#                 "head_git_commit_tag": [],
#                 "index": "0",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "NULL": 1,
#                         "PASS": 19
#                     },
#                     "builds": {
#                         "valid": 3
#                     },
#                     "tests": {
#                         "FAIL": 227,
#                         "MISS": 2,
#                         "PASS": 260,
#                         "SKIP": 44
#                     }
#                 },
#                 "tree_name": "arm64"
#             },
#             {
#                 "git_repository_branch": "for-next",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/broonie/regmap.git",
#                 "head_git_commit_hash": "78798d8875315a374ac7f0e076094a9198a5edda",
#                 "head_git_commit_name": "v6.13-rc7-15-g78798d887531",
#                 "head_git_commit_tag": [],
#                 "index": "1",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "PASS": 20
#                     },
#                     "builds": {
#                         "valid": 3
#                     },
#                     "tests": {
#                         "FAIL": 8,
#                         "MISS": 1,
#                         "PASS": 266,
#                         "SKIP": 36
#                     }
#                 },
#                 "tree_name": "broonie-regmap"
#             },
#             {
#                 "git_repository_branch": "for-next",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/broonie/regulator.git",
#                 "head_git_commit_hash": "5754b3acbe28cd93056e000ca239123f600a3b4d",
#                 "head_git_commit_name": "v6.13-rc7-16-g5754b3acbe28",
#                 "head_git_commit_tag": [],
#                 "index": "2",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "FAIL": 2,
#                         "PASS": 17
#                     },
#                     "builds": {
#                         "valid": 3
#                     },
#                     "tests": {
#                         "FAIL": 227,
#                         "PASS": 267,
#                         "SKIP": 44
#                     }
#                 },
#                 "tree_name": "broonie-regulator"
#             },
#             {
#                 "git_repository_branch": "for-next",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/broonie/sound.git",
#                 "head_git_commit_hash": "2367adc931673c5b671724ae86b6fe819aee9d8f",
#                 "head_git_commit_name": "asoc-v6.14-21-g2367adc93167",
#                 "head_git_commit_tag": [],
#                 "index": "3",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "PASS": 22
#                     },
#                     "builds": {
#                         "valid": 3
#                     },
#                     "tests": {
#                         "ERROR": 1,
#                         "FAIL": 220,
#                         "PASS": 147,
#                         "SKIP": 9
#                     }
#                 },
#                 "tree_name": "broonie-sound"
#             },
#             {
#                 "git_repository_branch": "for-next",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/broonie/spi.git",
#                 "head_git_commit_hash": "ff9e24437b18fa5a543c895f5b3d5108c67278d0",
#                 "head_git_commit_name": "v6.13-rc7-60-gff9e24437b18f",
#                 "head_git_commit_tag": [],
#                 "index": "4",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "PASS": 4
#                     },
#                     "builds": {
#                         "valid": 1
#                     },
#                     "tests": {}
#                 },
#                 "tree_name": "broonie-spi"
#             },
#             {
#                 "git_repository_branch": "clk-next",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/clk/linux.git",
#                 "head_git_commit_hash": "47b32b50ee28505eebd91eff40126483a15e5f4e",
#                 "head_git_commit_name": "qcom-clk-for-6.14-147-g47b32b50ee28",
#                 "head_git_commit_tag": [],
#                 "index": "5",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "NULL": 1,
#                         "PASS": 20
#                     },
#                     "builds": {
#                         "valid": 3
#                     },
#                     "tests": {
#                         "FAIL": 222,
#                         "NULL": 2,
#                         "PASS": 273,
#                         "SKIP": 44
#                     }
#                 },
#                 "tree_name": "clk"
#             },
#             {
#                 "git_repository_branch": "master",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
#                 "head_git_commit_hash": "95ec54a420b8f445e04a7ca0ea8deb72c51fe1d3",
#                 "head_git_commit_name": "v6.13-918-g95ec54a420b8",
#                 "head_git_commit_tag": [],
#                 "index": "6",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "PASS": 20
#                     },
#                     "builds": {
#                         "valid": 3
#                     },
#                     "tests": {
#                         "ERROR": 2,
#                         "FAIL": 387,
#                         "MISS": 3,
#                         "NULL": 2,
#                         "PASS": 518,
#                         "SKIP": 44
#                     }
#                 },
#                 "tree_name": "mainline"
#             },
#             {
#                 "git_repository_branch": "main",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net-next.git",
#                 "head_git_commit_hash": "cf33d96f50903214226b379b3f10d1f262dae018",
#                 "head_git_commit_name": "v6.13-rc7-1620-gcf33d96f50903",
#                 "head_git_commit_tag": [],
#                 "index": "7",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "NULL": 1,
#                         "PASS": 3
#                     },
#                     "builds": {
#                         "valid": 1
#                     },
#                     "tests": {}
#                 },
#                 "tree_name": "net-next"
#             },
#             {
#                 "git_repository_branch": "master",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git",
#                 "head_git_commit_hash": "f066b5a6c7a06adfb666b7652cc99b4ff264f4ed",
#                 "head_git_commit_name": "next-20250121",
#                 "head_git_commit_tag": [
#                     "next-20250121"
#                 ],
#                 "index": "8",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "PASS": 4
#                     },
#                     "builds": {
#                         "valid": 3
#                     },
#                     "tests": {
#                         "FAIL": 4,
#                         "MISS": 2,
#                         "PASS": 1
#                     }
#                 },
#                 "tree_name": "next"
#             },
#             {
#                 "git_repository_branch": "pending-fixes",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git",
#                 "head_git_commit_hash": "9e5c7d574d79f927cb3353c4437eaf532e904115",
#                 "head_git_commit_name": "v6.13-939-g9e5c7d574d79",
#                 "head_git_commit_tag": [],
#                 "index": "9",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "PASS": 4
#                     },
#                     "builds": {
#                         "valid": 3
#                     },
#                     "tests": {
#                         "FAIL": 166,
#                         "NULL": 1,
#                         "PASS": 255
#                     }
#                 },
#                 "tree_name": "next"
#             },
#             {
#                 "git_repository_branch": "testing",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm.git",
#                 "head_git_commit_hash": "69bbfd3a203eff79eacc8a02b3660deaa55624bc",
#                 "head_git_commit_name": "acpi-6.13-rc8-131-g69bbfd3a203e",
#                 "head_git_commit_tag": [],
#                 "index": "10",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "NULL": 1,
#                         "PASS": 19
#                     },
#                     "builds": {
#                         "valid": 3
#                     },
#                     "tests": {
#                         "FAIL": 227,
#                         "PASS": 267,
#                         "SKIP": 44
#                     }
#                 },
#                 "tree_name": "pm"
#             },
#             {
#                 "git_repository_branch": "master",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/geert/renesas-devel.git",
#                 "head_git_commit_hash": "d65183bfb94f5627b12a23700e03808b46ca9981",
#                 "head_git_commit_name": "renesas-devel-2025-01-21-v6.13",
#                 "head_git_commit_tag": [
#                     "renesas-devel-2025-01-21-v6.13"
#                 ],
#                 "index": "11",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "PASS": 4
#                     },
#                     "builds": {
#                         "valid": 1
#                     },
#                     "tests": {}
#                 },
#                 "tree_name": "renesas"
#             },
#             {
#                 "git_repository_branch": "for-next",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/soc/soc.git",
#                 "head_git_commit_hash": "fcf4173cc889f5a246d51a3c425f11d32ce615fc",
#                 "head_git_commit_name": "v6.13-rc7-832-gfcf4173cc889",
#                 "head_git_commit_tag": [],
#                 "index": "12",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "PASS": 20
#                     },
#                     "builds": {
#                         "valid": 3
#                     },
#                     "tests": {
#                         "FAIL": 227,
#                         "MISS": 1,
#                         "PASS": 265,
#                         "SKIP": 43
#                     }
#                 },
#                 "tree_name": "soc"
#             },
#             {
#                 "git_repository_branch": "linux-6.6.y",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git",
#                 "head_git_commit_hash": "3b4299ff7a25480d96c5e9a84b879e5193447d28",
#                 "head_git_commit_name": "v6.6.73",
#                 "head_git_commit_tag": [
#                     "v6.6.73"
#                 ],
#                 "index": "13",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "NULL": 1,
#                         "PASS": 3
#                     },
#                     "builds": {
#                         "valid": 2
#                     },
#                     "tests": {
#                         "ERROR": 1,
#                         "FAIL": 30,
#                         "PASS": 2
#                     }
#                 },
#                 "tree_name": "stable"
#             },
#             {
#                 "git_repository_branch": "master",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git",
#                 "head_git_commit_hash": "e6609f8bea4a5d16e6b1648d55e0c5a24cffbe96",
#                 "head_git_commit_name": "v6.13-1225-ge6609f8bea4a5",
#                 "head_git_commit_tag": [],
#                 "index": "14",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "PASS": 4
#                     },
#                     "builds": {
#                         "valid": 1
#                     },
#                     "tests": {}
#                 },
#                 "tree_name": "tip"
#             },
#             {
#                 "git_repository_branch": "next",
#                 "git_repository_url": "https://git.kernel.org/pub/scm/linux/kernel/git/ulfh/mmc.git",
#                 "head_git_commit_hash": "20a0c37e44063997391430c4ae09973e9cbc3911",
#                 "head_git_commit_name": "mmc-v6.13-rc2-2-27-g20a0c37e44063",
#                 "head_git_commit_tag": [],
#                 "index": "15",
#                 "is_selected": null,
#                 "selected_commit_status": {
#                     "boots": {
#                         "NULL": 1,
#                         "PASS": 19
#                     },
#                     "builds": {
#                         "valid": 3
#                     },
#                     "tests": {
#                         "FAIL": 224,
#                         "NULL": 3,
#                         "PASS": 268,
#                         "SKIP": 44
#                     }
#                 },
#                 "tree_name": "ulfh"
#             }
#         ]
#     }
# }
