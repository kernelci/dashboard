from typing import Literal
from kernelCI_app.models import Builds, Checkouts, Incidents, Issues, Tests

type TableNames = Literal["issues", "checkouts", "builds", "tests", "incidents"]
type TableModels = Issues | Checkouts | Builds | Tests | Incidents

MODEL_MAP: dict[TableNames, TableModels] = {
    "issues": Issues,
    "checkouts": Checkouts,
    "builds": Builds,
    "tests": Tests,
    "incidents": Incidents,
}
