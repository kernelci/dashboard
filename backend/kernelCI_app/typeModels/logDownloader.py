from typing import List, Optional
from pydantic import BaseModel


class LogData(BaseModel):
    specific_log_url: Optional[str]
    file_name: Optional[str]
    file_size: Optional[str]
    date: Optional[str]


class LogDownloaderQueryParameters(BaseModel):
    log_download_url: str


class LogDownloaderResponse(BaseModel):
    log_files: List[LogData]
