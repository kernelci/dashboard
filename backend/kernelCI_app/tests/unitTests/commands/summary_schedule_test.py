import pytest

from kernelCI import settings


@pytest.mark.skipif(settings.SKIP_CRONJOBS, reason="Cron jobs are disabled")
@pytest.mark.parametrize("origin", ["maestro", "microsoft"])
def test_scheduled_checkout_summary_records_sent_mail(origin):
    expected = {
        "--action=summary",
        f"--summary-origins={origin}",
        "--send",
        "--update-storage",
    }
    assert any(len(job) > 2 and expected.issubset(job[2]) for job in settings.CRONJOBS)
