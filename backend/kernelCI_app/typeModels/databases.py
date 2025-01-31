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


type Origin = str
type Timestamp = str

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
type Build__InputFiles = Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]
type Build__OutputFiles = Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]

type Test__Id = str
type Test__Status = Optional[DatabaseStatusValues]
type Test__Duration = Optional[float]
type Test__Path = Optional[str]
type Test__StartTime = Optional[datetime]
type Test__EnvironmentCompatible = Optional[List[str]]
