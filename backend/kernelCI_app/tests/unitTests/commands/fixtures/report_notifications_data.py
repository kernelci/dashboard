from datetime import datetime, timezone

from kernelCI import settings

FIXTURES_DIR = (
    settings.BASE_DIR / "kernelCI_app" / "tests" / "unitTests" / "commands" / "fixtures"
)
ISSUE_BUILD_REPORT_EXAMPLE_FILEPATH = FIXTURES_DIR / "issue_build_report_example.txt"
ISSUE_BOOT_REPORT_EXAMPLE_FILEPATH = FIXTURES_DIR / "issue_boot_report_example.txt"
TEST_REPORT_EXAMPLE_FILEPATH = FIXTURES_DIR / "test_report_example.txt"

# Fixed timestamps so the rendered fixtures stay deterministic.
_FAIL_TIME = datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc)
_LAST_PASS_TIME = datetime(2026, 5, 30, 9, 0, tzinfo=timezone.utc)

_HEAD_COMMIT = "ddd664bbff63e09e7a7f9acae9c43605d4cf185f"
_LAST_PASS_COMMIT = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"

# Fixed Message-ID so the lore link in the fixtures stays deterministic.
MESSAGE_ID = "<20260601120000.123456-1@kernelci.org>"


def make_build_issue(*, with_range: bool = True):
    """Returns an (issue, incidents) pair for a build regression report.

    When with_range is False the incident has no last passing commit, which
    is how the regzbot block is omitted in the rendered report.
    """
    issue = {
        "tree_name": "mainline",
        "git_repository_branch": "master",
        "comment": (
            "include/linux/signal.h:160:1: error: array index 2 is past the end "
            "of the array (that has type 'unsigned long[2]') [-Werror,-Warray-bounds] "
            "in lib/maple_tree.o (lib/maple_tree.c) [logspec:kbuild,kbuild.compiler.error]"
        ),
        "id": "maestro:98c2d110d805d1a864a89edd1e2c447175476af8",
        "git_repository_url": (
            "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
        ),
        "git_commit_hash": _HEAD_COMMIT,
        "git_commit_tags": [],
        "misc": {
            "logspec": {
                "error": {
                    "log_excerpt": (
                        "include/linux/signal.h:160:1: error: array index 2 is past "
                        "the end of the array [-Werror,-Warray-bounds]\n"
                        "  160 | _SIG_SET_BINOP(sigandsets, _sig_and)\n"
                        "fatal error: too many errors emitted, stopping now\n"
                        "20 errors generated.\n"
                    )
                }
            }
        },
    }
    incident = {
        "id": "maestro:6a2202cf2cc72b6e94c25e88",
        "config_name": "defconfig+allmodconfig+CONFIG_FRAME_WARN=2048",
        "config_url": "https://files.kernelci.org/maestro/config",
        "architecture": "arm",
        "compiler": "clang-21",
    }
    if with_range:
        incident["last_pass_commit"] = _LAST_PASS_COMMIT
    return issue, [incident]


def make_boot_issue(*, with_range: bool = True):
    """Returns an (issue, incidents) pair for a boot regression report."""
    issue = {
        "tree_name": "mainline",
        "git_repository_branch": "master",
        "comment": "Kernel panic - not syncing: Attempted to kill init!",
        "id": "maestro:0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c",
        "git_repository_url": (
            "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
        ),
        "git_commit_hash": _HEAD_COMMIT,
        "git_commit_tags": ["v6.16-rc1"],
        "misc": {
            "logspec": {
                "error": {
                    "log_excerpt": (
                        "[    2.512362] Run /sbin/init as init process\n"
                        "[    2.514426] Kernel panic - not syncing: Attempted "
                        "to kill init! exitcode=0x00000004\n"
                        "[    2.515282] CPU: 1 PID: 1 Comm: init Not tainted "
                        "6.16.0-rc1 #1\n"
                        "[    2.515684] Hardware name: Radxa ROCK 3A (DT)\n"
                        "[    2.516028] Call trace:\n"
                        "[    2.516216]  dump_backtrace+0x9c/0x100\n"
                        "[    2.516517]  panic+0x188/0x384\n"
                    )
                }
            }
        },
    }
    incident = {
        "id": "maestro:boot-7c8d9e0f1a2b",
        "platform": "rk3568-rock-3a",
        "environment_compatible": ["radxa,rock-3a", "rockchip,rk3568"],
        "platform_count": 5,
        "oldest_timestamp": _FAIL_TIME,
        "path": "boot",
        "last_pass_id": "maestro:boot-1a2b3c4d5e6f",
        "last_pass": _LAST_PASS_TIME,
        "last_pass_commit": _LAST_PASS_COMMIT if with_range else None,
    }
    return issue, [incident]


def make_test(*, with_range: bool = True):
    """Returns a test dict for a standalone test regression report."""
    return {
        "tree_name": "mainline",
        "git_repository_branch": "master",
        "path": "kselftest.net.fib_tests",
        "platform": "rk3568-rock-3a",
        "git_repository_url": (
            "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
        ),
        "git_commit_hash": _HEAD_COMMIT,
        "git_commit_tags": ["v6.16-rc1"],
        "id": "maestro:test-2b3c4d5e6f7a",
        "status": "FAIL",
        "start_time": _FAIL_TIME,
        "log_url": "https://files.kernelci.org/maestro/test/log.txt",
        "status_history": "✅ → ✅ → ❌",
        "environment_compatible": ["radxa,rock-3a", "rockchip,rk3568"],
        "config_name": "defconfig",
        "architecture": "arm64",
        "compiler": "gcc-12",
        "log_excerpt": "not ok 1 selftests: net: fib_tests.sh\n",
        "last_pass_commit": _LAST_PASS_COMMIT if with_range else None,
    }
