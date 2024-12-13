from pydantic import BaseModel, Field
from typing import Dict, Optional, Union

class PostBody(BaseModel):
    origin: str = Field(default="maestro")
    startTimestampInSeconds: Union[str, int]
    endTimestampInSeconds: Union[str, int]
    selectedCommits: Dict[str, str]
    filter: Optional[Dict]
