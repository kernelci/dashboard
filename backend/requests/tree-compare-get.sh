http 'http://localhost:8000/api/tree/linux/master/compare' \
  origin==maestro \
  hash_a==abc1234567890abcdef1234567890abcdef12 \
  hash_b==def5678901234abcdef5678901234abcdef56

# HTTP/1.1 200 OK
# {
#     "treeName": "linux",
#     "branch": "master",
#     "gitUrl": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
#     "summary": {
#         "builds": { "sideA": { "pass": 0, "fail": 0, "inconclusive": 0 }, ... },
#         "boots": { ... },
#         "tests": { ... }
#     },
#     "groups": {
#         "builds": [],
#         "boots": [],
#         "tests": []
#     }
# }
