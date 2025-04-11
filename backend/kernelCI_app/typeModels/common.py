from typing import Optional

from pydantic import BaseModel

from kernelCI_app.helpers.logger import log_message


class StatusCount(BaseModel):
    PASS: Optional[int] = 0
    ERROR: Optional[int] = 0
    FAIL: Optional[int] = 0
    SKIP: Optional[int] = 0
    MISS: Optional[int] = 0
    DONE: Optional[int] = 0
    NULL: Optional[int] = 0

    def increment(self, status: Optional[str]) -> None:
        if status is None:
            status = "NULL"

        try:
            setattr(self, status.upper(), getattr(self, status.upper()) + 1)
        except AttributeError:
            log_message(f"Unknown status: {status}")
