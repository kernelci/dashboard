from pydantic import BaseModel


class LabMetricsData(BaseModel):
    builds: int
    boots: int
    tests: int
    origin: str


class BuildIncidentsByOrigin(BaseModel):
    total: int
    new_regressions: int


class MetricsReportData(BaseModel):
    n_checkouts: int
    n_builds: int
    n_tests: int
    n_issues: int
    n_incidents: int
    build_incidents_by_origin: dict[str, BuildIncidentsByOrigin]
    lab_maps: dict[str, LabMetricsData]
