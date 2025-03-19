http 'localhost:8000/api/issue/?&intervalInDays=1&culpritCode=true'

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 27282
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Thu, 20 Feb 2025 11:51:56 GMT
# Expires: Thu, 20 Feb 2025 11:51:56 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "issues":[
#        {
#           "field_timestamp":"2025-03-21T05:50:33.654300Z",
#           "id":"maestro:cd18b383b75d152345cbe08983013da942678433",
#           "comment":" NULL pointer dereference at virtual address 0000000000000030 [logspec:generic_linux_boot,linux.kernel.null_pointer_dereference]",
#           "origin":"maestro",
#           "version":1,
#           "culprit_code":true,
#           "culprit_tool":false,
#           "culprit_harness":false
#        },
#        {
#           "field_timestamp":"2025-03-20T19:02:01.275697Z",
#           "id":"redhat:issue_3652",
#           "comment":"networking/netfilter/upstream_test/nftables  upstream-binary-nftables-tests-shell kernel warning net/core/flow_dissector.c",
#           "origin":"redhat",
#           "version":1742488543,
#           "culprit_code":true,
#           "culprit_tool":false,
#           "culprit_harness":false
#        },
#        {
#           "field_timestamp":"2025-03-21T11:22:57.073931Z",
#           "id":"redhat:issue_3585",
#           "comment":"[RHEL10] [internal-testsuite] perf-pipe-recording-and-injection-test FAIL",
#           "origin":"redhat",
#           "version":1741311124,
#           "culprit_code":true,
#           "culprit_tool":false,
#           "culprit_harness":false
#        },
       
#     ],
#     "extras":{
#        "redhat:issue_3492":{
#           "first_seen":"2025-02-12T13:00:01.018238Z",
#           "git_commit_hash":null,
#           "git_repository_url":null,
#           "git_repository_branch":null,
#           "git_commit_name":null,
#           "tree_name":null
#        },
#        "maestro:e602fca280d85d8e603f7c0aff68363bb0cd7993":{
#           "first_seen":"2025-01-21T00:24:05.705873Z",
#           "git_commit_hash":"d73a4602e973e9e922f00c537a4643907a547ade",
#           "git_repository_url":"https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net-next.git",
#           "git_repository_branch":"main",
#           "git_commit_name":"pm-6.13-rc8-1598-gd73a4602e973",
#           "tree_name":"net-next"
#        },
#        "maestro:da694c56147298d223ee432ad8d6a8ee311b773a":{
#           "first_seen":"2025-01-21T00:22:10.827866Z",
#           "git_commit_hash":"d73a4602e973e9e922f00c537a4643907a547ade",
#           "git_repository_url":"https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net-next.git",
#           "git_repository_branch":"main",
#           "git_commit_name":"pm-6.13-rc8-1598-gd73a4602e973",
#           "tree_name":"net-next"
#        }
#     }
#  }