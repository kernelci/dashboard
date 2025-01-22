from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime

FAIL_STATUS = "FAIL"
ERROR_STATUS = "ERROR"
MISS_STATUS = "MISS"
PASS_STATUS = "PASS"

failure_status_list = [ERROR_STATUS, FAIL_STATUS, MISS_STATUS]

# "NULL" must be added manually because the database return None
type StatusValues = Literal["FAIL", "PASS", "SKIP", "ERROR", "MISS", "NULL"]

type DatabaseStatusValues = Literal["FAIL", "PASS", "SKIP", "ERROR", "MISS"]


class Issues(BaseModel):
    field_timestamp: Optional[datetime] = Field(None, alias="_timestamp")
    id: str
    version: int
    origin: str
    report_url: Optional[str] = None
    report_subject: Optional[str] = None
    culprit_code: Optional[bool] = None
    culprit_tool: Optional[bool] = None
    culprit_harness: Optional[bool] = None
    build_valid: Optional[bool] = None
    test_status: Optional[str] = None
    comment: Optional[str] = None
    misc: Optional[Dict] = None


class Checkouts(BaseModel):
    field_timestamp: Optional[datetime] = Field(None, alias="_timestamp")
    id: str
    origin: str
    tree_name: Optional[str] = None
    git_repository_url: Optional[str] = None
    git_commit_hash: Optional[str] = None
    git_commit_name: Optional[str] = None
    git_repository_branch: Optional[str] = None
    patchset_files: Optional[Dict] = None
    patchset_hash: Optional[str] = None
    message_id: Optional[str] = None
    comment: Optional[str] = None
    start_time: Optional[datetime] = None
    contacts: Optional[Dict] = None
    log_url: Optional[str] = None
    log_excerpt: Optional[str] = None
    valid: Optional[bool] = None
    misc: Optional[Dict] = None


class Builds(BaseModel):
    field_timestamp: Optional[datetime] = Field(None, alias="_timestamp")
    checkout: Checkouts
    id: str
    origin: str
    comment: Optional[str] = None
    start_time: Optional[datetime] = None
    duration: Optional[float] = None
    architecture: Optional[str] = None
    command: Optional[str] = None
    compiler: Optional[str] = None
    input_files: Optional[Dict] = None
    output_files: Optional[Dict] = None
    config_name: Optional[str] = None
    config_url: Optional[str] = None
    log_url: Optional[str] = None
    log_excerpt: Optional[str] = None
    valid: Optional[bool] = None
    misc: Optional[Dict] = None


class Tests(BaseModel):
    field_timestamp: Optional[datetime] = Field(None, alias="_timestamp")
    build: Builds
    id: str
    origin: str
    environment_comment: Optional[str] = None
    environment_compatible: Optional[List[str]] = Field(default_factory=list)
    environment_misc: Optional[Dict] = None
    path: Optional[str] = None
    comment: Optional[str] = None
    log_url: Optional[str] = None

    log_excerpt: Optional[str] = None
    status: Optional[DatabaseStatusValues] = None
    waived: Optional[bool] = None
    start_time: Optional[datetime] = None
    duration: Optional[float] = None
    output_files: Optional[Dict] = None
    misc: Optional[Dict] = None


class Incidents(BaseModel):
    field_timestamp: Optional[datetime] = Field(None, alias="_timestamp")
    id: str
    origin: str
    issue: Issues
    issue_version: int
    build: Builds
    test: Tests
    present: Optional[bool] = None
    comment: Optional[str] = None
    misc: Optional[Dict] = None
