from pydantic import BaseModel, Field

from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.metrics_notifications import (
    BuildIncidentsCount,
    LabMetricsData,
    MetricsReportData,
    TopIssue,
)

DEFAULT_METRICS_START_DAYS_AGO = 7
DEFAULT_METRICS_END_DAYS_AGO = 0


class MetricsQueryParameters(BaseModel):
    start_days_ago: int = Field(
        default=DEFAULT_METRICS_START_DAYS_AGO,
        ge=0,
        description=DocStrings.METRICS_START_DAYS_AGO_DESCRIPTION,
    )
    end_days_ago: int = Field(
        default=DEFAULT_METRICS_END_DAYS_AGO,
        ge=0,
        description=DocStrings.METRICS_END_DAYS_AGO_DESCRIPTION,
    )


class MetricsResponse(BaseModel):
    n_trees: int
    n_checkouts: int
    n_builds: int
    n_tests: int
    n_issues: int
    n_incidents: int
    build_incidents_by_origin: dict[str, BuildIncidentsCount]
    top_issues_by_origin: dict[str, list[TopIssue]]
    lab_maps: dict[str, LabMetricsData]
    prev_n_trees: int
    prev_n_checkouts: int
    prev_n_builds: int
    prev_n_tests: int
    prev_lab_maps: dict[str, LabMetricsData]


def metrics_report_data_to_response(data: MetricsReportData) -> MetricsResponse:
    return MetricsResponse(
        n_trees=data.n_trees,
        n_checkouts=data.n_checkouts,
        n_builds=data.n_builds,
        n_tests=data.n_tests,
        n_issues=data.n_issues,
        n_incidents=data.n_incidents,
        build_incidents_by_origin=data.build_incidents_by_origin,
        top_issues_by_origin={
            origin: list(issues.values())
            for origin, issues in data.top_issues_by_origin.items()
        },
        lab_maps=data.lab_maps,
        prev_n_trees=data.prev_n_trees,
        prev_n_checkouts=data.prev_n_checkouts,
        prev_n_builds=data.prev_n_builds,
        prev_n_tests=data.prev_n_tests,
        prev_lab_maps=data.prev_lab_maps,
    )
