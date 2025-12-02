from datetime import datetime, timedelta, timezone
from kernelCI_app.management.commands.helpers.common import setup_jinja_template


def generate_metrics_report() -> None:
    template = setup_jinja_template("metrics_report.txt.j2")

    mock_data = {
        "start_datetime": (datetime.now(timezone.utc) - timedelta(days=7)).strftime(
            "%Y-%m-%d %H:%M %Z"
        ),
        "end_datetime": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M %Z"),
        "build_incidents_by_origin": {
            "origin1": {
                "total": 30,
                "new_regressions": 5,
            },
            "origin2": {
                "total": 500,
                "new_regressions": 253,
            },
        },
        "lab_maps": {
            "lab1": {
                "builds": 5,
                "boots": 2,
                "tests": 0,
            },
            "lab2": {
                "builds": 0,
                "boots": 4,
                "tests": 10,
            },
        },
        "lab_origins": {
            "lab1": "origin1",
            "lab2": "origin2",
        },
        "n_checkouts": 12,
        "n_builds": 40,
        "n_tests": 6000,
        "n_issues": 53,
        "n_incidents": 530,
    }

    print(template.render(**mock_data))

    return
