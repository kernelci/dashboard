from typing import TypedDict

from pydantic import BaseModel


class LabMetricsData(BaseModel):
    builds: int
    boots: int
    tests: int


class BuildIncidentsCount(TypedDict):
    total_incidents: int
    n_new_issues: int
    n_existing_issues: int
    n_total_issues: int


class TopIssue(TypedDict):
    id: str
    version: int
    comment: str
    total_incidents: int


class MetricsReportData(BaseModel):
    # Current interval
    n_trees: int
    n_checkouts: int
    n_builds: int
    n_tests: int
    n_issues: int
    n_incidents: int
    build_incidents_by_origin: dict[str, BuildIncidentsCount]
    # top_issues = origin -> (issue_id, version) -> TopIssue
    top_issues_by_origin: dict[str, dict[tuple[str, int], TopIssue]]
    lab_maps: dict[str, LabMetricsData]
    # Previous interval (for comparison)
    prev_n_trees: int
    prev_n_checkouts: int
    prev_n_builds: int
    prev_n_tests: int
    prev_lab_maps: dict[str, LabMetricsData]
