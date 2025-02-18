from pydantic import RootModel
from kernelCI_app.typeModels.issues import Issue


class DetailsIssuesResponse(RootModel):
    root: list[Issue]
