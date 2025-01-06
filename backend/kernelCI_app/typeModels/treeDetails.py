from pydantic import BaseModel


class TreeLatestPathParameters(BaseModel):
    tree_name: str
    branch: str
