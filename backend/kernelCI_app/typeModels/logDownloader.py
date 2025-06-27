from typing import List, Optional
from pydantic import BaseModel, Field


class LogData(BaseModel):
    specific_log_url: Optional[str]
    file_name: Optional[str]
    file_size: Optional[str]
    date: Optional[str]


class LogDownloaderQueryParameters(BaseModel):
    log_download_url: str = Field(description="URL of the log to be downloaded")


class LogDownloaderResponse(BaseModel):
    log_files: List[LogData]
