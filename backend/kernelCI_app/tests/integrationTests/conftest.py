import pytest


@pytest.fixture(autouse=True)
def recompute_runs_as_dev(monkeypatch):
    # This process is classified as staging, which no-ops these commands.
    monkeypatch.setattr(
        "kernelCI_app.management.commands.recompute_hardware_daily.get_running_instance",
        lambda: None,
    )
    monkeypatch.setattr(
        "kernelCI_app.management.commands.recompute_lab_daily.get_running_instance",
        lambda: None,
    )
