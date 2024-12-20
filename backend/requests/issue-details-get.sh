http 'http://localhost:8000/api/issue/maestro:26cab82e27e6b4a7e883e14b72220126b0206e4e/version/0'

# HTTP/1.1 200 OK
# Cache-Control: max-age=0
# Content-Length: 3651
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Fri, 20 Dec 2024 16:05:15 GMT
# Expires: Fri, 20 Dec 2024 16:05:15 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "build_valid": null,
#     "comment": "[logspec:generic_linux_boot] linux.kernel.warning WARNING at drivers/of/base.c:106 of_bus_n_addr_cells+0x88/0xdc",
#     "culprit_code": true,
#     "culprit_harness": false,
#     "culprit_tool": false,
#     "field_timestamp": "2024-12-19T13:12:05.527Z",
#     "id": "maestro:26cab82e27e6b4a7e883e14b72220126b0206e4e",
#     "misc": {
#         "logspec": {
#             "error": {
#                 "call_trace": [
#                     "of_bus_n_addr_cells+0x88/0xdc (P)",
#                     "of_n_addr_cells+0x1c/0x28",
#                     "of_bus_default_count_cells+0x28/0x50",
#                     "__of_get_address+0xb0/0x1c0",
#                     "__of_address_to_resource+0x44/0x1fc",
#                     "of_address_to_resource+0x18/0x24",
#                     "of_device_alloc+0x78/0x198",
#                     "of_platform_device_create_pdata+0x54/0x124",
#                     "of_platform_bus_create+0x158/0x39c",
#                     "of_platform_populate+0x74/0x108",
#                     "of_platform_default_populate_init+0x94/0x108",
#                     "do_one_initcall+0x80/0x1c4",
#                     "kernel_init_freeable+0x1c8/0x290",
#                     "kernel_init+0x20/0x1d8",
#                     "ret_from_fork+0x10/0x20"
#                 ],
#                 "error_summary": "WARNING at drivers/of/base.c:106 of_bus_n_addr_cells+0x88/0xdc",
#                 "error_type": "linux.kernel.warning",
#                 "hardware": "Google juniper sku16 board (DT)",
#                 "location": "drivers/of/base.c:106 of_bus_n_addr_cells+0x88/0xdc",
#                 "log_excerpt": "[    0.121406] Missing '#address-cells' in /firmware\n[    0.121483] WARNING: CPU: 0 PID: 1 at drivers/of/base.c:106 of_bus_n_addr_cells+0x88/0xdc\n[    0.121505] Modules linked in:\n[    0.121518] CPU: 0 UID: 0 PID: 1 Comm: swapper/0 Not tainted 6.13.0-rc3 #1\n[    0.121529] Hardware name: Google juniper sku16 board (DT)\n[    0.121537] pstate: 60000005 (nZCv daif -PAN -UAO -TCO -DIT -SSBS BTYPE=--)\n[    0.121548] pc : of_bus_n_addr_cells+0x88/0xdc\n[    0.121557] lr : of_bus_n_addr_cells+0x88/0xdc\n[    0.121565] sp : ffff80008008ba60\n[    0.121571] x29: ffff80008008ba60 x28: 0000000000000000 x27: ffffa9659c259050\n[    0.121586] x26: ffff2372ff7b7e80 x25: ffffa9659b97cbf0 x24: ffff80008008bba0\n[    0.121599] x23: ffff80008008bb9c x22: ffff2372ff7b7c90 x21: ffffa9659c0582c8\n[    0.121613] x20: ffffa9659d155f11 x19: ffff2372ff7b7c90 x18: 0000000000000006\n[    0.121627] x17: 0000000000000100 x16: 00000000effec225 x15: 0720072007200720\n[    0.121640] x14: 0765077207610777 x13: ffffa9659cc847e0 x12: 00000000000001c5\n[    0.121654] x11: 0000000000000097 x10: ffffa9659ccdc7e0 x9 : ffffa9659cc847e0\n[    0.121668] x8 : 00000000ffffefff x7 : ffffa9659ccdc7e0 x6 : 80000000fffff000\n[    0.121681] x5 : 000000000000bff4 x4 : 0000000000000000 x3 : 0000000000000000\n[    0.121694] x2 : 0000000000000000 x1 : 0000000000000000 x0 : ffff2372c0138000\n[    0.121708] Call trace:\n[    0.121715]  of_bus_n_addr_cells+0x88/0xdc (P)\n[    0.121726]  of_n_addr_cells+0x1c/0x28\n[    0.121735]  of_bus_default_count_cells+0x28/0x50\n[    0.121749]  __of_get_address+0xb0/0x1c0\n[    0.121760]  __of_address_to_resource+0x44/0x1fc\n[    0.121772]  of_address_to_resource+0x18/0x24\n[    0.121783]  of_device_alloc+0x78/0x198\n[    0.121792]  of_platform_device_create_pdata+0x54/0x124\n[    0.121803]  of_platform_bus_create+0x158/0x39c\n[    0.121812]  of_platform_populate+0x74/0x108\n[    0.121822]  of_platform_default_populate_init+0x94/0x108\n[    0.121835]  do_one_initcall+0x80/0x1c4\n[    0.121847]  kernel_init_freeable+0x1c8/0x290\n[    0.121859]  kernel_init+0x20/0x1d8\n[    0.121872]  ret_from_fork+0x10/0x20\n",
#                 "signature_fields": {
#                     "error_summary": "WARNING at drivers/of/base.c:106 of_bus_n_addr_cells+0x88/0xdc",
#                     "error_type": "linux.kernel.warning",
#                     "location": "drivers/of/base.c:106 of_bus_n_addr_cells+0x88/0xdc"
#                 }
#             },
#             "parser": "generic_linux_boot",
#             "version": "1.0.0"
#         }
#     },
#     "origin": "maestro",
#     "report_subject": null,
#     "report_url": null,
#     "test_status": "FAIL",
#     "version": 0
# }
