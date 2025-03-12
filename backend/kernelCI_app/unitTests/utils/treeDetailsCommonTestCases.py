from kernelCI_app.typeModels.treeDetails import TreeQueryParameters


UNEXISTENT_TREE = {
    "id": "invalid id",
    "params": {
        "query": TreeQueryParameters(
            origin="maestro",
            git_url="https://android.googlesource.com/kernel/common",
            git_branch="android-mainline",
        )
    },
}

INVALID_QUERY_PARAMS = {
    "id": "fb482243c16ebfe8776fcd52223351b4061c1729",
    "params": {"query": TreeQueryParameters(origin="", git_url="", git_branch="")},
}

# https://dashboard.kernelci.org/tree/fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba?ti%7Cc=ASB-2025-03-05_mainline-1867-gfdf4d20b86285&ti%7Cch=fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba&ti%7Cgb=android-mainline&ti%7Cgu=https%3A%2F%2Fandroid.googlesource.com%2Fkernel%2Fcommon&ti%7Ct=android
ANDROID_MAESTRO_MAINLINE = {
    "id": "fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba",
    "params": {
        "query": TreeQueryParameters(
            origin="maestro",
            git_url="https://android.googlesource.com/kernel/common",
            git_branch="android-mainline",
        )
    },
}

# https://dashboard.kernelci.org/tree/33040a50cdaec186c13ef3f7b9c9b668d8e32637?o=broonie&ti%7Cc=&ti%7Cch=bb2eb9603973cb353faa8e780b304d3537220228&ti%7Cgb=pending-fixes&ti%7Cgu=https%3A%2F%2Fgit.kernel.org%2Fpub%2Fscm%2Flinux%2Fkernel%2Fgit%2Fnext%2Flinux-next.git&ti%7Ct=next
NEXT_PENDING_FIXES_BROONIE = {
    "id": "33040a50cdaec186c13ef3f7b9c9b668d8e32637",
    "params": {
        "query": TreeQueryParameters(
            origin="broonie",
            git_url="https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git",
            git_branch="pending-fixes",
        ),
        "filters": {
            "valid": "true",
            "config_name": "defconfig",
            "architecture": "x86_64",
        },
    },
}

# https://dashboard.kernelci.org/tree/4b60a3c25e8793adfb1d92f8e4888321ae416fed?ti%7Cc=v6.13-1652-g4b60a3c25e879&ti%7Cch=4b60a3c25e8793adfb1d92f8e4888321ae416fed&ti%7Cgb=for-kernelci&ti%7Cgu=https%3A%2F%2Fgit.kernel.org%2Fpub%2Fscm%2Flinux%2Fkernel%2Fgit%2Fbroonie%2Fmisc.git&ti%7Ct=broonie-misc
BROONIE_MISC_BROONIE = {
    "id": "4b60a3c25e8793adfb1d92f8e4888321ae416fed",
    "params": {
        "query": TreeQueryParameters(
            origin="maestro",
            git_url="https://git.kernel.org/pub/scm/linux/kernel/git/broonie/misc.git",
            git_branch="for-kernelci",
        ),
        "filters": {
            "boot.status": "PASS",
            "config_name": "multi_v7_defconfig",
            "test.hardware": "fsl,imx6q-sabrelite",
            "test.status": "SKIP",
        },
    },
}
