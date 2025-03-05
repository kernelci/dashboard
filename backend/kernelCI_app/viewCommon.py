from kernelCI_app.typeModels.commonDetails import BuildHistoryItem


# TODO: Change this for a pydantic model
def create_default_build_status() -> dict:
    return {"PASS": 0, "FAIL": 0, "NULL": 0}


def create_details_build_summary(builds: BuildHistoryItem) -> dict:
    build_summ = create_default_build_status()
    config_summ = {}
    arch_summ = {}

    for build in builds:
        status_key = build.status
        build_summ[status_key] += 1

        if config := build.config_name:
            status = config_summ.get(config)
            if not status:
                status = create_default_build_status()
                config_summ[config] = status
            status[status_key] += 1

        if arch := build.architecture:
            status = arch_summ.setdefault(arch, create_default_build_status())
            status[status_key] += 1
            compiler = build.compiler
            if compiler and compiler not in status.setdefault("compilers", []):
                status["compilers"].append(compiler)

    return {
        "builds": build_summ,
        "configs": config_summ,
        "architectures": arch_summ,
    }
