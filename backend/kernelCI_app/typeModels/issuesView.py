from typing import List
from pydantic import RootModel
from kernelCI_app.typeModels.issues import Issue


class IssuesResponse(RootModel):
    root: List[Issue]
