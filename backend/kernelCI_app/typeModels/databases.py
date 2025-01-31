from typing import List, Optional, Dict, Literal, Any, Union
from datetime import datetime

FAIL_STATUS = "FAIL"
ERROR_STATUS = "ERROR"
MISS_STATUS = "MISS"
PASS_STATUS = "PASS"
NULL_STATUS = "NULL"

failure_status_list = [ERROR_STATUS, FAIL_STATUS, MISS_STATUS]

# "NULL" must be added manually because the database return None
type StatusValues = Literal["FAIL", "PASS", "SKIP", "ERROR", "MISS", "NULL", "DONE"]

type DatabaseStatusValues = Literal["FAIL", "PASS", "SKIP", "ERROR", "MISS", "DONE"]

type Jsonb = Union[Dict[str, Any], List[Dict[str, Any]]]

type Origin = str
type Timestamp = datetime

type Checkout__Id = str
type Checkout__TreeName = Optional[str]
type Checkout__GitCommitHash = Optional[str]
type Checkout__GitCommitName = Optional[str]
type Checkout__GitCommitTags = Optional[List[str]]

type Build__Id = str
type Build__Architecture = Optional[str]
type Build__ConfigName = Optional[str]
type Build__Valid = Optional[bool]
type Build__StartTime = Optional[datetime]
type Build__Duration = Optional[float]
type Build__Compiler = Optional[str]
type Build__Command = Optional[str]
type Build__Comment = Optional[str]
type Build__LogExcerpt = Optional[str]
type Build__LogUrl = Optional[str]
type Build__InputFiles = Optional[Jsonb]
type Build__OutputFiles = Optional[Jsonb]

type Test__Id = str
type Test__Status = Optional[DatabaseStatusValues]
type Test__Duration = Optional[float]
type Test__Path = Optional[str]
type Test__StartTime = Optional[datetime]
type Test__EnvironmentCompatible = Optional[List[str]]

type Issue__Id = str
type Issue__Version = int
type Issue__ReportUrl = Optional[str]
type Issue__ReportSubject = Optional[str]
type Issue__CulpritCode = Optional[bool]
type Issue__CulpritTool = Optional[bool]
type Issue__CulpritHarness = Optional[bool]
type Issue__BuildValid = Optional[bool]
type Issue__TestStatus = Optional[str]
type Issue__Comment = Optional[str]
type Issue__Misc = Optional[Jsonb]
