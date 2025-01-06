from typing import TypedDict
from kernelCI_app.helpers.build import build_status_map


class BuildDict(TypedDict):
    valid: str
    config_name: str
    architecture: str
    compiler: str


def create_default_build_status():
    return {"valid": 0, "invalid": 0, "null": 0}


def create_details_build_summary(builds: list[BuildDict]):
    build_summ = create_default_build_status()
    config_summ = {}
    arch_summ = {}

    for build in builds:
        status_key = build_status_map[build["valid"]]
        build_summ[status_key] += 1

        if config := build["config_name"]:
            status = config_summ.get(config)
            if not status:
                status = create_default_build_status()
                config_summ[config] = status
            status[status_key] += 1

        if arch := build["architecture"]:
            status = arch_summ.setdefault(arch, create_default_build_status())
            status[status_key] += 1
            compiler = build["compiler"]
            if compiler and compiler not in status.setdefault("compilers", []):
                status["compilers"].append(compiler)

    return {
        "builds": build_summ,
        "configs": config_summ,
        "architectures": arch_summ,
    }
