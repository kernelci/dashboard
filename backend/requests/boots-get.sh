# Database tested - `playground_kcidb`
# This should be empty
# http 'http://localhost:8000/api/tree/a-git-commit-hash-that-clearly-does-not-exist/boot/'
# This should find something
http 'http://localhost:8000/api/tree/1dd28064d4164a4dc9096fd1a7990d2de15f2bb6/tests/'

# {
#   "statusCounts": {
#     "FAIL": 2,
#     "MISS": 1,
#     "PASS": 1,
#     "ERROR": 1
#   },
#   "errorCounts": {
#     "FAIL": 2,
#     "MISS": 1,
#     "ERROR": 1
#   },
#   "configStatusCounts": {
#     "defconfig": {
#       "FAIL": 2,
#       "PASS": 1
#     },
#     "multi_v7_defconfig": {
#       "MISS": 1
#     },
#     "null": {
#       "ERROR": 1
#     }
#   },
#   "testHistory": [
#     {
#       "start_time": "2024-07-06T00:58:20.149Z",
#       "status": "FAIL"
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
#       "start_time": "2024-07-06T00:56:56.659Z",
#       "status": "FAIL"
#     },
#     {
#       "start_time": "2024-07-06T00:26:44.970Z",
#       "status": "ERROR"
#     }
#   ],
#   "errorCountPerArchitecture": {
#     "arm64": 2,
#     "arm": 1,
#     "null": 1
#   },
#   "compilersPerArchitecture": {
#     "arm64": [
#       "gcc-12"
#     ],
#     "arm": [
#       "gcc-12"
#     ],
#     "null": [
#       null
#     ]
#   },
#   "platformsWithError": [
#     "mt8183-kukui-jacuzzi-juniper-sku16",
#     "kubernetes",
#     "bcm2711-rpi-4-b",
#     "bcm2836-rpi-2-b"
#   ],
#   "errorMessageCounts": {
#     "unknown error": 4,
#     "No time left for remaining 1 retries. 2 retries out of 3 failed for auto-login-action": 2,
#     "Node timed-out": 2
#   }
# }