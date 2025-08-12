from kernelCI_app.typeModels.treeDetails import (
    DirectTreePathParameters,
    DirectTreeQueryParameters,
    TreeQueryParameters,
)


UNEXISTENT_TREE = {
    "id": "invalid id",
    "params": {
        "query": TreeQueryParameters(
            origin="maestro",
            git_url="https://android.googlesource.com/kernel/common",
            git_branch="android-mainline",
        ),
    },
    "direct_params": {
        "query": DirectTreeQueryParameters(origin="maestro"),
        "path": DirectTreePathParameters(
            tree_name="android", git_branch="android-mainline", commit_hash="invalid id"
        ),
    },
}

INVALID_QUERY_PARAMS = {
    "id": "fb482243c16ebfe8776fcd52223351b4061c1729",
    "params": {"query": TreeQueryParameters(origin="", git_url="", git_branch="")},
    "direct_params": {
        "query": DirectTreeQueryParameters(origin=" "),
        "path": DirectTreePathParameters(
            tree_name=" ", git_branch=" ", commit_hash=" "
        ),
    },
}

# https://dashboard.kernelci.org/tree/fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba?tri%7Cc=ASB-2025-03-05_mainline-1867-gfdf4d20b86285&tri%7Cch=fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba&tri%7Cgb=android-mainline&tri%7Cgu=https%3A%2F%2Fandroid.googlesource.com%2Fkernel%2Fcommon&tri%7Ct=android
# https://dashboard.kernelci.org/tree/android/android-mainline/fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba
ANDROID_MAESTRO_MAINLINE = {
    "id": "fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba",
    "params": {
        "query": TreeQueryParameters(
            origin="maestro",
            git_url="https://android.googlesource.com/kernel/common",
            git_branch="android-mainline",
        )
    },
    "direct_params": {
        "query": DirectTreeQueryParameters(origin="maestro"),
        "path": DirectTreePathParameters(
            tree_name="android",
            git_branch="android-mainline",
            commit_hash="fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba",
        ),
    },
}

# https://dashboard.kernelci.org/tree/33040a50cdaec186c13ef3f7b9c9b668d8e32637?o=broonie&tri%7Cc=&tri%7Cch=bb2eb9603973cb353faa8e780b304d3537220228&tri%7Cgb=pending-fixes&tri%7Cgu=https%3A%2F%2Fgit.kernel.org%2Fpub%2Fscm%2Flinux%2Fkernel%2Fgit%2Fnext%2Flinux-next.git&tri%7Ct=next
# https://dashboard.kernelci.org/tree/next/pending-fixes/33040a50cdaec186c13ef3f7b9c9b668d8e32637?o=broonie
NEXT_PENDING_FIXES_BROONIE = {
    "id": "33040a50cdaec186c13ef3f7b9c9b668d8e32637",
    "params": {
        "query": TreeQueryParameters(
            origin="broonie",
            git_url="https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git",
            git_branch="pending-fixes",
        ),
        "filters": {
            "build.status": "PASS",
            "config_name": "defconfig",
            "architecture": "x86_64",
        },
    },
    "direct_params": {
        "query": DirectTreeQueryParameters(origin="broonie"),
        "path": DirectTreePathParameters(
            tree_name="next",
            git_branch="pending-fixes",
            commit_hash="33040a50cdaec186c13ef3f7b9c9b668d8e32637",
        ),
    },
}

# https://dashboard.kernelci.org/tree/4b60a3c25e8793adfb1d92f8e4888321ae416fed?tri%7Cc=v6.13-1652-g4b60a3c25e879&tri%7Cch=4b60a3c25e8793adfb1d92f8e4888321ae416fed&tri%7Cgb=for-kernelci&tri%7Cgu=https%3A%2F%2Fgit.kernel.org%2Fpub%2Fscm%2Flinux%2Fkernel%2Fgit%2Fbroonie%2Fmisc.git&tri%7Ct=broonie-misc
# https://dashboard.kernelci.org/tree/broonie-misc/for-kernelci/4b60a3c25e8793adfb1d92f8e4888321ae416fed
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
    "direct_params": {
        "query": DirectTreeQueryParameters(origin="maestro"),
        "path": DirectTreePathParameters(
            tree_name="broonie-misc",
            git_branch="for-kernelci",
            commit_hash="4b60a3c25e8793adfb1d92f8e4888321ae416fed",
        ),
    },
}
