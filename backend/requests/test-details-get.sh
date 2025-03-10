http 'http://localhost:8000/api/test/maestro:67a182c5661a7bc8748b9905'

# HTTP/1.1 200 OK
# Allow: GET, HEAD, OPTIONS
# Cache-Control: max-age=0
# Content-Length: 18677
# Content-Type: application/json
# Cross-Origin-Opener-Policy: same-origin
# Date: Mon, 10 Mar 2025 19:59:02 GMT
# Expires: Mon, 10 Mar 2025 19:59:02 GMT
# Referrer-Policy: same-origin
# Server: WSGIServer/0.2 CPython/3.12.7
# Vary: Accept, Cookie, origin
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# {
#     "architecture": "x86_64",
#     "build_id": "maestro:dummy_67a17d87661a7bc8748b90cd_x86_64",
#     "compiler": null,
#     "config_name": null,
#     "environment_compatible": null,
#     "environment_misc": {
#         "platform": "kubernetes"
#     },
#     "field_timestamp": "2025-02-04T03:02:01.190150Z",
#     "git_commit_hash": "170c9fb62732486d54f4876cfee81654f217364c",
#     "git_commit_tags": [],
#     "git_repository_branch": "android15-6.6",
#     "git_repository_url": "https://android.googlesource.com/kernel/common",
#     "id": "maestro:67a182c5661a7bc8748b9905",
#     "log_excerpt": "n_order_2\naction_order_1\n    ok 12 kunit_resource_test_action_ordering\n# kunit-resource-test: pass:12 fail:0 skip:0 total:12\n# Totals: pass:12 fail:0 skip:0 total:12\nok 13 kunit-resource-test\n    KTAP version 1\n    # Subtest: kunit-log-test\n    # module: kunit_test\n    1..2\nput this in log.\nthis too.\nadd to suite log.\nalong with this.\n    ok 1 kunit_log_test\n    # kunit_log_newline_test: Add newline\n    ok 2 kunit_log_newline_test\n# kunit-log-test: pass:2 fail:0 skip:0 total:2\n# Totals: pass:2 fail:0 skip:0 total:2\nok 14 kunit-log-test\n    KTAP version 1\n    # Subtest: kunit_status\n    # module: kunit_test\n    1..2\n    ok 1 kunit_status_set_failure_test\n    ok 2 kunit_status_mark_skipped_test\n# kunit_status: pass:2 fail:0 skip:0 total:2\n# Totals: pass:2 fail:0 skip:0 total:2\nok 15 kunit_status\n    KTAP version 1\n    # Subtest: kunit_current\n    # module: kunit_test\n    1..2\n    ok 1 kunit_current_test\n    # fake test: lib/kunit/kunit-test.c:641: This should make `fake` test fail.\n    ok 2 kunit_current_fail_test\n# kunit_current: pass:2 fail:0 skip:0 total:2\n# Totals: pass:2 fail:0 skip:0 total:2\nok 16 kunit_current\n    KTAP version 1\n    # Subtest: string-stream-test\n    # module: string_stream_test\n    1..3\n    ok 1 string_stream_test_empty_on_creation\n    ok 2 string_stream_test_not_empty_after_add\n    ok 3 string_stream_test_get_string\n# string-stream-test: pass:3 fail:0 skip:0 total:3\n# Totals: pass:3 fail:0 skip:0 total:3\nok 17 string-stream-test\n    # example: initializing suite\n    KTAP version 1\n    # Subtest: example\n    # module: kunit_example_test\n    1..7\n    # example_simple_test: initializing\n    # example_simple_test: cleaning up\n    ok 1 example_simple_test\n    # example_skip_test: initializing\n    # example_skip_test: You should not see a line below.\n    # example_skip_test: cleaning up\n    ok 2 example_skip_test # SKIP this test should be skipped\n    # example_mark_skipped_test: initializing\n    # example_mark_skipped_test: You should see a line below.\n    # example_mark_skipped_test: You should see this line.\n    # example_mark_skipped_test: cleaning up\n    ok 3 example_mark_skipped_test # SKIP this test should be skipped\n    # example_all_expect_macros_test: initializing\n    # example_all_expect_macros_test: cleaning up\n    ok 4 example_all_expect_macros_test\n    # example_static_stub_test: initializing\n    # example_static_stub_test: cleaning up\n    ok 5 example_static_stub_test\n        KTAP version 1\n        # Subtest: example_params_test\n    # example_params_test: initializing\n    # example_params_test: cleaning up\n        ok 1 example value 2\n    # example_params_test: initializing\n    # example_params_test: cleaning up\n        ok 2 example value 1\n    # example_params_test: initializing\n    # example_params_test: cleaning up\n        ok 3 example value 0 # SKIP unsupported param value\n    # example_params_test: pass:2 fail:0 skip:1 total:3\n    ok 6 example_params_test\n    # example_slow_test: initializing\n    # example_slow_test: cleaning up\n    # example_slow_test.speed: slow\n    ok 7 example_slow_test\n    # example: exiting suite\n# example: pass:5 fail:0 skip:2 total:7\n# Totals: pass:6 fail:0 skip:3 total:9\nok 18 example\n    KTAP version 1\n    # Subtest: bitfields\n    # module: bitfield_kunit\n    1..2\n    ok 1 test_bitfields_constants\n    ok 2 test_bitfields_variables\n# bitfields: pass:2 fail:0 skip:0 total:2\n# Totals: pass:2 fail:0 skip:0 total:2\nok 19 bitfields\n    KTAP version 1\n    # Subtest: checksum\n    # module: checksum_kunit\n    1..3\n    ok 1 test_csum_fixed_random_inputs\n    ok 2 test_csum_all_carry_inputs\n    ok 3 test_csum_no_carry_inputs\n# checksum: pass:3 fail:0 skip:0 total:3\n# Totals: pass:3 fail:0 skip:0 total:3\nok 20 checksum\n    KTAP version 1\n    # Subtest: list-kunit-test\n    # module: list_test\n    1..39\n    ok 1 list_test_list_init\n    ok 2 list_test_list_add\n    ok 3 list_test_list_add_tail\n    ok 4 list_test_list_del\n    ok 5 list_test_list_replace\n    ok 6 list_test_list_replace_init\n    ok 7 list_test_list_swap\n    ok 8 list_test_list_del_init\n    ok 9 list_test_list_del_init_careful\n    ok 10 list_test_list_move\n    ok 11 list_test_list_move_tail\n    ok 12 list_test_list_bulk_move_tail\n    ok 13 list_test_list_is_head\n    ok 14 list_test_list_is_first\n    ok 15 list_test_list_is_last\n    ok 16 list_test_list_empty\n    ok 17 list_test_list_empty_careful\n    ok 18 list_test_list_rotate_left\n    ok 19 list_test_list_rotate_to_front\n    ok 20 list_test_list_is_singular\n    ok 21 list_test_list_cut_position\n    ok 22 list_test_list_cut_before\n    ok 23 list_test_list_splice\n    ok 24 list_test_list_splice_tail\n    ok 25 list_test_list_splice_init\n    ok 26 list_test_list_splice_tail_init\n    ok 27 list_test_list_entry\n    ok 28 list_test_list_entry_is_head\n    ok 29 list_test_list_first_entry\n    ok 30 list_test_list_last_entry\n    ok 31 list_test_list_first_entry_or_null\n    ok 32 list_test_list_next_entry\n    ok 33 list_test_list_prev_entry\n    ok 34 list_test_list_for_each\n    ok 35 list_test_list_for_each_prev\n    ok 36 list_test_list_for_each_safe\n    ok 37 list_test_list_for_each_prev_safe\n    ok 38 list_test_list_for_each_entry\n    ok 39 list_test_list_for_each_entry_reverse\n# list-kunit-test: pass:39 fail:0 skip:0 total:39\n# Totals: pass:39 fail:0 skip:0 total:39\nok 21 list-kunit-test\n    KTAP version 1\n    # Subtest: hlist\n    # module: list_test\n    1..18\n    ok 1 hlist_test_init\n    ok 2 hlist_test_unhashed\n    ok 3 hlist_test_unhashed_lockless\n    ok 4 hlist_test_del\n    ok 5 hlist_test_del_init\n    ok 6 hlist_test_add\n    ok 7 hlist_test_fake\n    ok 8 hlist_test_is_singular_node\n    ok 9 hlist_test_empty\n    ok 10 hlist_test_move_list\n    ok 11 hlist_test_entry\n    ok 12 hlist_test_entry_safe\n    ok 13 hlist_test_for_each\n    ok 14 hlist_test_for_each_safe\n    ok 15 hlist_test_for_each_entry\n    ok 16 hlist_test_for_each_entry_continue\n    ok 17 hlist_test_for_each_entry_from\n    ok 18 hlist_test_for_each_entry_safe\n# hlist: pass:18 fail:0 skip:0 total:18\n# Totals: pass:18 fail:0 skip:0 total:18\nok 22 hlist\n    KTAP version 1\n    # Subtest: klist\n    # module: list_test\n    1..8\n    ok 1 klist_test_add_tail\n    ok 2 klist_test_add_head\n    ok 3 klist_test_add_behind\n    ok 4 klist_test_add_before\n    ok 5 klist_test_del_refcount_greater_than_zero\n    ok 6 klist_test_del_refcount_zero\n    ok 7 klist_test_remove\n    ok 8 klist_test_node_attached\n# klist: pass:8 fail:0 skip:0 total:8\n# Totals: pass:8 fail:0 skip:0 total:8\nok 23 klist\n    KTAP version 1\n    # Subtest: hashtable\n    # module: hashtable_test\n    1..9\n    ok 1 hashtable_test_hash_init\n    ok 2 hashtable_test_hash_empty\n    ok 3 hashtable_test_hash_hashed\n    ok 4 hashtable_test_hash_add\n    ok 5 hashtable_test_hash_del\n    ok 6 hashtable_test_hash_for_each\n    ok 7 hashtable_test_hash_for_each_safe\n    ok 8 hashtable_test_hash_for_each_possible\n    ok 9 hashtable_test_hash_for_each_possible_safe\n# hashtable: pass:9 fail:0 skip:0 total:9\n# Totals: pass:9 fail:0 skip:0 total:9\nok 24 hashtable\n    KTAP version 1\n    # Subtest: bits-test\n    # module: test_bits\n    1..3\n    ok 1 genmask_test\n    ok 2 genmask_ull_test\n    ok 3 genmask_input_check_test\n# bits-test: pass:3 fail:0 skip:0 total:3\n# Totals: pass:3 fail:0 skip:0 total:3\nok 25 bits-test\n    KTAP version 1\n    # Subtest: cmdline\n    # module: cmdline_kunit\n    1..4\n    ok 1 cmdline_test_noint\n    ok 2 cmdline_test_lead_int\n    ok 3 cmdline_test_tail_int\n    ok 4 cmdline_test_range\n# cmdline: pass:4 fail:0 skip:0 total:4\n# Totals: pass:4 fail:0 skip:0 total:4\nok 26 cmdline\n    KTAP version 1\n    # Subtest: slub_test\n    # module: slub_kunit\n    1..6\n    ok 1 test_clobber_zone\n    ok 2 test_next_pointer\n    ok 3 test_first_word\n    ok 4 test_clobber_50th_byte\n    ok 5 test_clobber_redzone_free\nstackdepot: allocating hash table of 65536 entries via kvcalloc\n    ok 6 test_kmalloc_redzone_access\n# slub_test: pass:6 fail:0 skip:0 total:6\n# Totals: pass:6 fail:0 skip:0 total:6\nok 27 slub_test\n    KTAP version 1\n    # Subtest: memcpy\n    # module: memcpy_kunit\n    1..7\n    # memset_test: ok: memset() direct assignment\n    # memset_test: ok: memset() complete overwrite\n    # memset_test: ok: memset() middle overwrite\n    # memset_test: ok: memset() argument side-effects\n    # memset_test: ok: memset() memset_after()\n    # memset_test: ok: memset() memset_startat()\n    ok 1 memset_test\n    # memcpy_test: ok: memcpy() static initializers\n    # memcpy_test: ok: memcpy() direct assignment\n    # memcpy_test: ok: memcpy() complete overwrite\n    # memcpy_test: ok: memcpy() middle overwrite\n    # memcpy_test: ok: memcpy() argument side-effects\n    ok 2 memcpy_test\ninput: ImExPS/2 Generic Explorer Mouse as /devices/platform/i8042/serio1/input/input2\n    # memcpy_large_test.speed: slow\n    ok 3 memcpy_large_test\n    # memmove_test: ok: memmove() static initializers\n    # memmove_test: ok: memmove() direct assignment\n    # memmove_test: ok: memmove() complete overwrite\n    # memmove_test: ok: memmove() middle overwrite\n    # memmove_test: ok: memmove() argument side-effects\n    # memmove_test: ok: memmove() overlapping write\n    # memmove_test.speed: slow\n    ok 4 memmove_test\n    # memmove_large_test.speed: slow\n    ok 5 memmove_large_test\n    # memmove_overlap_test.speed: slow\n    ok 6 memmove_overlap_test\n    ok 7 strtomem_test\n# memcpy: pass:7 fail:0 skip:0 total:7\n# Totals: pass:7 fail:0 skip:0 total:7\nok 28 memcpy\n    KTAP version 1\n    # Subtest: is_signed_type\n    # module: is_signed_type_kunit\n    1..1\n    ok 1 is_signed_type_test\nok 29 is_signed_type\n    KTAP version 1\n    # Subtest: overflow\n    # module: overflow_kunit\n    1..21\n    # u8_u8__u8_overflow_test: 18 u8_u8__u8 arithmetic tests finished\n    ok 1 u8_u8__u8_overflow_test\n    # s8_s8__s8_overflow_test: 19 s8_s8__s8 arithmetic tests finished\n    ok 2 s8_s8__s8_overflow_test\n    # u16_u16__u16_overflow_test: 17 u16_u16__u16 arithmetic tests finished\n    ok 3 u16_u16__u16_overflow_test\n    # s16_s16__s16_overflow_test: 17 s16_s16__s16 arithmetic tests finished\n    ok 4 s16_s16__s16_overflow_test\n    # u32_u32__u32_overflow_test: 17 u32_u32__u32 arithmetic tests finished\n    ok 5 u32_u32__u32_overflow_test\n    # s32_s32__s32_overflow_test: 17 s32_s32__s32 arithmetic tests finished\n    ok 6 s32_s32__s32_overflow_test\n    # u64_u64__u64_overflow_test: 17 u64_u64__u64 arithmetic tests finished\n    ok 7 u64_u64__u64_overflow_test\n    # s64_s64__s64_overflow_test: 21 s64_s64__s64 arithmetic tests finished\n    ok 8 s64_s64__s64_overflow_test\n    # u32_u32__int_overflow_test: 2 u32_u32__int arithmetic tests finished\n    ok 9 u32_u32__int_overflow_test\n    # u32_u32__u8_overflow_test: 3 u32_u32__u8 arithmetic tests finished\n    ok 10 u32_u32__u8_overflow_test\n    # u8_u8__int_overflow_test: 3 u8_u8__int arithmetic tests finished\n    ok 11 u8_u8__int_overflow_test\n    # int_int__u8_overflow_test: 3 int_int__u8 arithmetic tests finished\n    ok 12 int_int__u8_overflow_test\n    # shift_sane_test: 36 sane shift tests finished\n    ok 13 shift_sane_test\n    # shift_overflow_test: 25 overflow shift tests finished\n    ok 14 shift_overflow_test\n    # shift_truncate_test: 27 truncate shift tests finished\n    ok 15 shift_truncate_test\n    # shift_nonsense_test: 25 nonsense shift tests finished\n    ok 16 shift_nonsense_test\n    # overflow_allocation_test: 11 allocation overflow tests finished\n    ok 17 overflow_allocation_test\n    # overflow_size_helpers_test: 43 overflow size helper tests finished\n    ok 18 overflow_size_helpers_test\n    # overflows_type_test: 658 overflows_type() tests finished\n    ok 19 overflows_type_test\n    # same_type_test: 0 __same_type() tests finished\n    ok 20 same_type_test\n    # castable_to_type_test: 103 castable_to_type() tests finished\n    ok 21 castable_to_type_test\n# overflow: pass:21 fail:0 skip:0 total:21\n# Totals: pass:21 fail:0 skip:0 total:21\nok 30 overflow\n    KTAP version 1\n    # Subtest: stackinit\n    # module: stackinit_kunit\n    1..65\n    ok 1 test_u8_zero\n    ok 2 test_u16_zero\n    ok 3 test_u32_zero\n    ok 4 test_u64_zero\n    ok 5 test_char_array_zero\n    ok 6 test_small_hole_zero\n    ok 7 test_big_hole_zero\n    ok 8 test_trailing_hole_zero\n    ok 9 test_packed_zero\n    ok 10 test_small_hole_dynamic_partial\n    ok 11 test_big_hole_dynamic_partial\n    ok 12 test_trailing_hole_dynamic_partial\n    ok 13 test_packed_dynamic_partial\n    ok 14 test_small_hole_assigned_dynamic_partial\n    ok 15 test_big_hole_assigned_dynamic_partial\n    ok 16 test_trailing_hole_assigned_dynamic_partial\n    ok 17 test_packed_assigned_dynamic_partial\n    ok 18 test_small_hole_static_partial\n    ok 19 test_big_hole_static_partial\n    ok 20 test_trailing_hole_static_partial\n    ok 21 test_packed_static_partial\n    ok 22 test_small_hole_static_all\n    ok 23 test_big_hole_static_all\n    ok 24 test_trailing_hole_static_all\n    ok 25 test_packed_static_all\n    ok 26 test_small_hole_dynamic_all\n    ok 27 test_big_hole_dynamic_all\n    ok 28 test_trailing_hole_dynamic_all\n    ok 29 test_packed_dynamic_all\n    ok 30 test_small_hole_runtime_partial\n    ok 31 test_big_hole_runtime_partial\n    ok 32 test_trailing_hole_runtime_partial\n    ok 33 test_packed_runtime_partial\n    ok 34 test_small_hole_runtime_all\n    ok 35 test_big_hole_runtime_all\n    ok 36 test_trailing_hole_runtime_all\n    ok 37 test_packed_runtime_all\n    ok 38 test_small_hole_assigned_static_partial\n    ok 39 test_big_hole_assigned_static_partial\n    ok 40 test_trailing_hole_assigned_static_partial\n    ok 41 test_packed_assigned_static_partial\n    ok 42 test_small_hole_assigned_static_all\n    ok 43 test_big_hole_assigned_static_all\n    ok 44 test_trailing_hole_assigned_static_all\n    ok 45 test_packed_assigned_static_all\n    ok 46 test_small_hole_assigned_dynamic_all\n    ok 47 test_big_hole_assigned_dynamic_all\n    ok 48 test_trailing_hole_assigned_dynamic_all\n    ok 49 test_packed_assigned_dynamic_all\n    ok 50 test_small_hole_assigned_copy # SKIP XFAIL uninit bytes: 3\n    ok 51 test_big_hole_assigned_copy # SKIP XFAIL uninit bytes: 124\n    ok 52 test_trailing_hole_assigned_copy # SKIP XFAIL uninit bytes: 7\n    ok 53 test_packed_assigned_copy\n    ok 54 test_u8_none\n    ok 55 test_u16_none\n    ok 56 test_u32_none\n    ok 57 test_u64_none\n    ok 58 test_char_array_none\n    ok 59 test_switch_1_none # SKIP XFAIL uninit bytes: 80\n    ok 60 test_switch_2_none # SKIP XFAIL uninit bytes: 12\n    ok 61 test_small_hole_none\n    ok 62 test_big_hole_none\n    ok 63 test_trailing_hole_none\n    ok 64 test_packed_none\n    ok 65 test_user\n# stackinit: pass:60 fail:0 skip:5 total:65\n# Totals: pass:60 fail:0 skip:5 total:65\nok 31 stackinit\n    KTAP version 1\n    # Subtest: strcat\n    # module: strcat_kunit\n    1..3\n    ok 1 strcat_test\n    ok 2 strncat_test\n    ok 3 strlcat_test\n# strcat: pass:3 fail:0 skip:0 total:3\n# Totals: pass:3 fail:0 skip:0 total:3\nok 32 strcat\n    KTAP version 1\n    # Subtest: strscpy\n    # module: strscpy_kunit\n    1..1\n    ok 1 strscpy_test\nok 33 strscpy\n    KTAP version 1\n    # Subtest: siphash\n    # module: siphash_kunit\n    1..1\n    ok 1 siphash_test\nok 34 siphash\n    KTAP version 1\n    # Subtest: qos-kunit-test\n    # module: qos_test\n    1..3\n    ok 1 freq_qos_test_min\n    ok 2 freq_qos_test_maxdef\n    ok 3 freq_qos_test_readd\n# qos-kunit-test: pass:3 fail:0 skip:0 total:3\n# Totals: pass:3 fail:0 skip:0 total:3\nok 35 qos-kunit-test\n    KTAP version 1\n    # Subtest: property-entry\n    # module: property_entry_test\n    1..7\n    ok 1 pe_test_uints\n    ok 2 pe_test_uint_arrays\n    ok 3 pe_test_strings\n    ok 4 pe_test_bool\n    ok 5 pe_test_move_inline_u8\n    ok 6 pe_test_move_inline_str\n    ok 7 pe_test_reference\n# property-entry: pass:7 fail:0 skip:0 total:7\n# Totals: pass:7 fail:0 skip:0 total:7\nok 36 property-entry\n    KTAP version 1\n    # Subtest: input_core\n    # module: input_test\n    1..4\ninput: Test input device as /devices/virtual/input/input3\n    ok 1 input_test_polling\ninput: Test input device as /devices/virtual/input/input4\n    ok 2 input_test_timestamp\ninput: Test input device as /devices/virtual/input/input5\n    ok 3 input_test_match_device_id\ninput: Test input device as /devices/virtual/input/input6\n    ok 4 input_test_grab\n# input_core: pass:4 fail:0 skip:0 total:4\n# Totals: pass:4 fail:0 skip:0 total:4\nok 37 input_core\nreboot: Restarting system\nreboot: machine restart\n",
#     "log_url": "https://kciapistagingstorage1.file.core.windows.net/production/kunit-x86_64-67a17e87661a7bc8748b9409/test_log?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D",
#     "misc": {
#         "arch": "x86_64",
#         "runtime": "k8s-gke-eu-west4"
#     },
#     "origin": "maestro",
#     "output_files": [
#         {
#             "name": "tarball",
#             "url": "https://kciapistagingstorage1.file.core.windows.net/production/linux-android-android15-6.6-android15-6.6.66_r00-80-g170c9fb627324.tar.gz?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D"
#         },
#         {
#             "name": "job_txt",
#             "url": "https://kciapistagingstorage1.file.core.windows.net/production/kunit-x86_64-67a17e87661a7bc8748b9409/job_txt?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D"
#         },
#         {
#             "name": "kunit_json",
#             "url": "https://kciapistagingstorage1.file.core.windows.net/production/kunit-x86_64-67a17e87661a7bc8748b9409/kunit_json?sv=2022-11-02&ss=f&srt=sco&sp=r&se=2026-10-18T13:36:18Z&st=2024-10-17T05:36:18Z&spr=https&sig=xFxYOOh5uXJWeN9I3YKAUvpGGQivo89HKZbD78gcxvc%3D"
#         }
#     ],
#     "path": "kunit.exec.siphash",
#     "start_time": "2025-02-04T03:00:21.480000Z",
#     "status": "PASS",
#     "tree_name": "android"
# }
