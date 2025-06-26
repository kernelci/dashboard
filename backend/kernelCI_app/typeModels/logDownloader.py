from typing import List, Optional
from pydantic import BaseModel, Field

from kernelCI_app.constants.localization import DocStrings


class LogData(BaseModel):
    specific_log_url: Optional[str]
    file_name: Optional[str]
    file_size: Optional[str]
    date: Optional[str]


class LogDownloaderQueryParameters(BaseModel):
    log_download_url: str = Field(description=DocStrings.LOG_DOWNLOADER_URL_DESCRIPTION)


class LogDownloaderResponse(BaseModel):
    log_files: List[LogData]
