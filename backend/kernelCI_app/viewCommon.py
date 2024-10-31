from typing import TypedDict
from kernelCI_app.utils import create_issue


class BuildDict(TypedDict):
    valid: str
    config_name: str
    architecture: str
    compiler: str


def create_default_build_status():
    return {"valid": 0, "invalid": 0, "null": 0}


def create_details_build_summary(builds: list[BuildDict]):
    status_map = {True: "valid", False: "invalid", None: "null"}

    build_summ = create_default_build_status()
    config_summ = {}
    arch_summ = {}

    for build in builds:
        status_key = status_map[build["valid"]]
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


def get_details_issue(record):
    return create_issue(
        issue_id=record["issue_id"],
        issue_comment=record["issue_comment"],
        issue_report_url=record["issue_report_url"],
    )
