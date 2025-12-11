from typing import Literal, Type
from kernelCI_app.models import Builds, Checkouts, Incidents, Issues, Tests

type TableNames = Literal["issues", "checkouts", "builds", "tests", "incidents"]
type TableModels = Issues | Checkouts | Builds | Tests | Incidents
type TableModelsClass = Type[Issues] | Type[Checkouts] | Type[Builds] | Type[
    Tests
] | Type[Incidents]

MODEL_MAP: dict[TableNames, TableModelsClass] = {
    "issues": Issues,
    "checkouts": Checkouts,
    "builds": Builds,
    "tests": Tests,
    "incidents": Incidents,
}
