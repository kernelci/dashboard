from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from kernelCI_cache.typeModels.databases import PossibleIssueType


class CustomIssue(BaseModel):
    id: str
    version: int
    kcidb_timestamp: datetime
    comment: Optional[str]
    type: PossibleIssueType
    notification_ignore: bool
