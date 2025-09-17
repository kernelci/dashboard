"""
Tree data fixtures for test factories.
"""

from datetime import datetime, timezone

TREE_DATA = {
    "a1c24ab822793eb513351686f631bd18952b7870": {  # ARM64_TREE
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git",
        "git_branch": "for-kernelci",
        "tree_name": "arm64",
        "start_time": None,
        "hardware_platform": None,
    },
    "ef143cc9d68aecf16ec4942e399e7699266b288f": {  # ANDROID_MAINLINE_TREE
        "origin": "maestro",
        "git_url": "https://android.googlesource.com/kernel/common",
        "git_branch": "android-mainline",
        "tree_name": "android",
        "start_time": None,
        "hardware_platform": None,
    },
    "fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba": {  # ANDROID_MAESTRO_MAINLINE
        "origin": "maestro",
        "git_url": "https://android.googlesource.com/kernel/common",
        "git_branch": "android-mainline",
        "tree_name": "android",
        "start_time": None,
        "hardware_platform": None,
    },
    "33040a50cdaec186c13ef3f7b9c9b668d8e32637": {  # NEXT_PENDING_FIXES_BROONIE
        "origin": "broonie",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git",
        "git_branch": "pending-fixes",
        "tree_name": "next",
        "start_time": None,
        "hardware_platform": None,
    },
    "4b60a3c25e8793adfb1d92f8e4888321ae416fed": {  # BROONIE_MISC_BROONIE
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/broonie/misc.git",
        "git_branch": "for-kernelci",
        "tree_name": "broonie-misc",
        "start_time": None,
        "hardware_platform": None,
    },
    "5b4ec6e1eb7603b6d86a172d77efdf75eb741e7e": {  # ALLWINNER_HARDWARE
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git",
        "git_branch": "for-kernelci",
        "tree_name": "arm64",
        "start_time": datetime.fromtimestamp(
            1741449600, timezone.utc
        ),  # allwinner,sun50i-a64
        "hardware_platform": "allwinner,sun50i-a64",
    },
    "0704a15b930cf97073ce091a0cd7ad32f2304329": {  # ALLWINNER_HARDWARE
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git",
        "git_branch": "for-kernelci",
        "tree_name": "arm64",
        "start_time": datetime.fromtimestamp(
            1741449600, timezone.utc
        ),  # allwinner,sun50i-a64
        "hardware_platform": "allwinner,sun50i-a64",
    },
    "fb482243c16ebfe8776fcd52223351b4061c1729": {  # INVALID_QUERY_PARAMS
        "origin": "maestro",
        "git_url": "https://android.googlesource.com/kernel/common",
        "git_branch": "android-mainline",
        "tree_name": "android",
        "start_time": None,
        "hardware_platform": None,
    },
    "google_juniper_checkout_001": {  # google_juniper_checkout_001
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
        "git_branch": "master",
        "tree_name": "google_mainline",
        "start_time": datetime.fromtimestamp(
            1740227400, timezone.utc
        ),  # google,juniper
        "hardware_platform": "google,juniper",
    },
    "amlogic_checkout_001": {  # amlogic_checkout_001
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/amlogic/linux.git",
        "git_branch": "master",
        "tree_name": "amlogic",
        "start_time": datetime.fromtimestamp(1741359600, timezone.utc),  # amlogic,g12b
        "hardware_platform": "amlogic,g12b",
    },
    "7e39477098b50156535c8f910fee50d6dac2a793": {  # android11-5.4
        "origin": "maestro",
        "git_url": "https://android.googlesource.com/kernel/common",
        "git_branch": "android11-5.4",
        "tree_name": "android",
        "start_time": datetime.fromtimestamp(1737487800, timezone.utc),  # android11-5.4
        "hardware_platform": "android11-5.4",
    },
    "4fd7634f32ffbb4fd4c09b757aa16327626a1749": {  # android12-5.10
        "origin": "maestro",
        "git_url": "https://android.googlesource.com/kernel/common",
        "git_branch": "android12-5.10",
        "tree_name": "android",
        "start_time": datetime.fromtimestamp(
            1737487800, timezone.utc
        ),  # android12-5.10
        "hardware_platform": "android12-5.10",
    },
    "f72ba1ba267f4c42adb82037e8614d7844badeb9": {  # android12-5.10-lts
        "origin": "maestro",
        "git_url": "https://android.googlesource.com/kernel/common",
        "git_branch": "android12-5.10-lts",
        "tree_name": "android",
        "start_time": datetime.fromtimestamp(
            1737487800, timezone.utc
        ),  # android12-5.10-lts
        "hardware_platform": "android12-5.10-lts",
    },
    "fluster_checkout_001": {
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
        "git_branch": "master",
        "tree_name": "fluster_mainline",
        "start_time": datetime.fromtimestamp(
            1741571363, timezone.utc
        ),  # 2025-03-10T01:49:23.064000Z
        "hardware_platform": "mt8195-cherry-tomato-r2",
    },
    "arm_juno_checkout_001": {
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git",
        "git_branch": "for-kernelci",
        "tree_name": "arm64",
        "start_time": datetime.fromtimestamp(1740232800, timezone.utc),  # arm,juno
        "hardware_platform": "arm,juno",
    },
    "aaeon_checkout_001": {
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
        "git_branch": "master",
        "tree_name": "aaeon_mainline",
        "start_time": datetime.fromtimestamp(
            1740241800, timezone.utc
        ),  # aaeon-UPN-EHLX4RE-A10-0864
        "hardware_platform": "aaeon-UPN-EHLX4RE-A10-0864",
    },
    "asus_checkout_001": {
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
        "git_branch": "master",
        "tree_name": "asus_mainline",
        "start_time": datetime.fromtimestamp(
            1741356000, timezone.utc
        ),  # asus-CM1400CXA-dalboz
        "hardware_platform": "asus-CM1400CXA-dalboz",
    },
    "failed_tests_checkout": {
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/failed_tests.git",
        "git_branch": "master",
        "tree_name": "failed_tests_mainline",
        "start_time": datetime.fromtimestamp(
            1741356000, timezone.utc
        ),  # failed_tests_build
        "hardware_platform": None,
    },
}
