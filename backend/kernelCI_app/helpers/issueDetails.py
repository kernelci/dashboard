from typing import Dict
from kernelCI_app.models import Issues


def fetch_latest_issue_version(*, issue_id: str) -> Dict:
    version_row = Issues.objects.values("version").filter(id=issue_id).order_by("-version").first()
    return version_row
