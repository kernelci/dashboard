"""
Issue data fixtures for test or build factories.
"""

ISSUE_TEST_DATA = {
    "maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573": {
        "version": 1,
        "build_ids": ["maestro:67b62592f7707533c0ff7a77"],  # ANDROID_MAINLINE_TREE
        "test_ids": [],
    },
    "maestro:87244933628a2612f39e6096115454f1e8bb3e1c": {
        "version": 1,
        "build_ids": ["maestro:67b62592f7707533c0ff7a99"],  # ARM64_TREE
        "test_ids": [],
    },
    "maestro:ee1cba21ee3fe47f21061725de689b638a9c431a": {
        "version": 1,
        "build_ids": ["maestro:67b62592f7707533c0ff7a95"],  # ARM64_TREE
        "test_ids": [],
    },
    "maestro:cb38e75d16f267781d5b085b9b2dbb390e2885c4": {
        "version": 1,
        "build_ids": ["maestro:67b62592f7707533c0ff7a94"],  # ARM64_TREE
        "test_ids": [],
    },
    "maestro:ae160f6f27192c3527b2e88faba35d85d27c285f": {
        "version": 1,
        "build_ids": [
            "maestro:dummy_67cb759a180183719578307e_x86_64"
        ],  # ANDROID_MAESTRO_MAINLINE
        "test_ids": [],
    },
    "maestro:e602fca280d85d8e603f7c0aff68363bb0cd7993": {
        "version": 1,
        "build_ids": ["redhat:1701576995-x86_64-kernel"],  # REDHAT_KERNEL
        "test_ids": [],
    },
    "broonie:bb2eb9603973cb353faa8e780b304d3537220228": {
        "version": 1,
        "build_ids": [],
        "test_ids": ["maestro:67bd70e6323b35c54a8824a0"],  # ARM64_TREE
    },
    "linaro:30MeoIqiN9rKm6s2lQLaThEnGHF": {
        "version": 1,
        "build_ids": [],
        "test_ids": ["test_issue_test"],
    },
}
