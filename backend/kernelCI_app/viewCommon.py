from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.commonDetails import (
    BaseBuildSummary,
    BuildArchitectures,
    BuildHistoryItem,
)


def _increment_status(var: StatusCount, status_key):
    """Increments a specific status_key (PASS, FAIL...) of a StatusCount var"""
    setattr(var, status_key, getattr(var, status_key) + 1)


def create_details_build_summary(builds: list[BuildHistoryItem]) -> BaseBuildSummary:
    status_summ = StatusCount()
    config_summ: dict[str, StatusCount] = {}
    arch_summ: dict[str, BuildArchitectures] = {}
    origin_summ: dict[str, StatusCount] = {}

    for build in builds:
        status_key = build.status
        _increment_status(status_summ, status_key)

        if config := build.config_name:
            status = config_summ.setdefault(config, StatusCount())
            _increment_status(status, status_key)

        if arch := build.architecture:
            status = arch_summ.setdefault(arch, BuildArchitectures())
            _increment_status(status, status_key)
            compiler = build.compiler
            if compiler and compiler not in status.compilers:
                status.compilers.append(compiler)

        if origin := build.origin:
            status = origin_summ.setdefault(origin, StatusCount())
            _increment_status(status, status_key)

    return BaseBuildSummary(
        status=status_summ,
        configs=config_summ,
        architectures=arch_summ,
        origins=origin_summ,
    )
