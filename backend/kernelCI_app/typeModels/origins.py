from pydantic import BaseModel

from kernelCI_app.typeModels.databases import Origin


class OriginsResponse(BaseModel):
    checkout_origins: list[Origin]
