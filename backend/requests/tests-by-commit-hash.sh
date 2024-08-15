# Database tested - `playground_kcidb`
# This should be empty
# http 'http://localhost:8000/api/tree/a-git-commit-hash-that-clearly-does-not-exist/boot/'
# This should find something
http 'http://localhost:8000/api/improv/0a33b8afe07a366222228559e4dd1de564dbdf13'

# {
#   "errorCounts": {
#     "MISS": 2,
#     "PASS": 1,
#     "ERROR": 1
#   },
#   "configCounts": {
#     "defconfig": 3,
#     "multi_v7_defconfig": 1
#   },
#   "bootHistory": [
#     {
#       "start_time": "2024-07-06T00:58:14.830Z",
#       "status": "MISS"
#     },
#     {
#       "start_time": "2024-07-06T00:48:55.924Z",
#       "status": "MISS"
#     },
#     {
#       "start_time": "2024-07-06T01:11:10.816Z",
#       "status": "PASS"
#     },
#     {
#       "start_time": "2024-07-06T00:56:49.278Z",
#       "status": "ERROR"
#     }
#   ],
#   "errorCountPerArchitecture": {
#     "arm64": 2,
#     "arm": 1
#   },
#   "compilersPerArchitecture": {
#     "arm64": [
#       "gcc-12"
#     ],
#     "arm": [
#       "gcc-12"
#     ]
#   },
#   "platforms": [
#     "bcm2836-rpi-2-b",
#     "meson-g12b-a311d-khadas-vim3",
#     "sc7180-trogdor-lazor-limozeen"
#   ],
#   "errorMessageCounts": {
#     "400 Client Error: Bad Request for url: https://lava.infra.foundries.io/api/v0.2/jobs/?format=json&limit=256": 1,
#     "No time left for remaining 1 retries. 2 retries out of 3 failed for auto-login-action": 1,
#     "Invalid TESTCASE signal": 1
#   }
# }

