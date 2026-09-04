http 'http://localhost:8000/api/tree/linux/master/compare/builds' \
  origin==maestro \
  hash_a==abc1234567890abcdef1234567890abcdef12 \
  hash_b==def5678901234abcdef5678901234abcdef56

# HTTP/1.1 200 OK
# {
#     "builds": [
#         {
#             "config_name": "defconfig",
#             "architecture": "arm64",
#             "compiler": "gcc-12",
#             "status_a": "PASS",
#             "status_b": "FAIL"
#         }
#     ]
# }
