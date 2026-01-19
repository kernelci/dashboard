from collections.abc import Callable
from typing import Optional, Dict, List, Tuple, TypedDict, Literal, Any, Union
from django.http import HttpRequest, HttpResponseBadRequest
import re
from kernelCI_app.constants.general import UNCATEGORIZED_STRING
from kernelCI_app.helpers.commonDetails import PossibleTabs
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.typeModels.databases import (
    StatusValues,
    failure_status_list,
    build_fail_status_list,
)
from kernelCI_app.typeModels.issues import (
    ISSUE_FILTER_OPTIONS,
    POSSIBLE_CULPRITS,
    IssueFilterOptions,
    PossibleIssueCulprits,
)
from kernelCI_app.utils import get_error_body_response
from kernelCI_app.constants.general import UNKNOWN_STRING

NULL_STRINGS = set(["null", UNKNOWN_STRING, "NULL"])


def is_status_failure(
    test_status: StatusValues, fail_list: list[StatusValues] = failure_status_list
) -> bool:
    return test_status in fail_list


def is_known_issue(issue_id: Optional[str], issue_version: Optional[int]) -> bool:
    return (
        issue_id is not None
        and issue_version is not None
        and issue_id is not UNCATEGORIZED_STRING
    )


def is_unknown_build_issue(
    issue_id: Optional[str],
    issue_version: Optional[int],
    incident_test_id: Optional[str],
) -> bool:
    is_unknown_issue = not is_known_issue(issue_id, issue_version)
    is_issue_from_build = incident_test_id is None
    return is_unknown_issue and is_issue_from_build


def is_exclusively_build_issue(
    issue_id: Optional[str],
    issue_version: Optional[int],
    incident_test_id: Optional[str],
) -> bool:
    is_known_issue_result = is_known_issue(issue_id, issue_version)
    is_exclusively_build_issue_result = (
        is_known_issue_result and incident_test_id is None
    )
    return is_exclusively_build_issue_result


def is_exclusively_test_issue(
    *,
    issue_id: Optional[str],
    issue_version: Optional[int],
    incident_test_id: Optional[str],
) -> bool:
    is_known_issue_result = is_known_issue(issue_id, issue_version)
    is_exclusively_test_issue_result = (
        is_known_issue_result and incident_test_id is not None
    )
    return is_exclusively_test_issue_result


def is_issue_from_test(
    *,
    incident_test_id: Optional[str],
    issue_id: Optional[str],
    issue_version: Optional[int],
) -> bool:
    is_known_issue_result = is_known_issue(
        issue_id=issue_id, issue_version=issue_version
    )
    is_possible_test_issue = incident_test_id is not None or not is_known_issue_result

    return is_possible_test_issue


def is_issue_from_build(
    *,
    issue_id: Optional[str],
    issue_version: Optional[int],
    incident_test_id: Optional[str],
) -> bool:
    is_known_issue_result = is_known_issue(
        issue_id=issue_id, issue_version=issue_version
    )
    is_possible_build_issue = incident_test_id is None or not is_known_issue_result

    return is_possible_build_issue


def verify_issue_in_filter(
    issue_filter_data: Union[Dict, str],
    issue_id: Optional[str],
    issue_version: Optional[int],
) -> bool:
    is_unknown_issue = False
    if issue_filter_data == UNCATEGORIZED_STRING:
        filter_issue_id = UNCATEGORIZED_STRING
        is_unknown_issue = True
    else:
        filter_issue_id, filter_issue_version = issue_filter_data

    is_issue_id_in_filter = filter_issue_id == issue_id
    is_issue_version_filter = is_unknown_issue or filter_issue_version == issue_version

    return is_issue_id_in_filter and is_issue_version_filter


def is_issue_filtered_out(
    *, issue_id: Optional[str], issue_filters: set, issue_version: Optional[int]
) -> bool:
    in_filter = any(
        verify_issue_in_filter(
            issue_filter_data=issue, issue_id=issue_id, issue_version=issue_version
        )
        for issue in issue_filters
    )
    return not in_filter


def should_filter_test_issue(
    *,
    issue_filters: set,
    issue_id: Optional[str],
    issue_version: Optional[int],
    incident_test_id: Optional[str],
) -> bool:
    has_issue_filter = len(issue_filters) > 0
    if not has_issue_filter:
        return False

    has_uncategorized_filter = UNCATEGORIZED_STRING in issue_filters

    is_exclusively_build_issue_result = is_exclusively_build_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )

    if is_exclusively_build_issue_result and has_uncategorized_filter:
        return False
    if is_exclusively_build_issue_result:
        issue_id = UNCATEGORIZED_STRING

    is_issue_filtered_out_result = is_issue_filtered_out(
        issue_id=issue_id, issue_version=issue_version, issue_filters=issue_filters
    )

    return is_issue_filtered_out_result


def should_filter_build_issue(
    *,
    issue_filters: set,
    issue_id: Optional[str],
    issue_version: Optional[int],
    incident_test_id: Optional[str],
    build_status: StatusValues,
) -> bool:
    has_issue_filter = len(issue_filters) > 0
    if not has_issue_filter:
        return False

    if not is_status_failure(build_status, build_fail_status_list):
        return True

    has_uncategorized_filter = UNCATEGORIZED_STRING in issue_filters

    is_exclusively_test_issue_result = is_exclusively_test_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )
    is_unknown_build_issue_result = is_unknown_build_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )

    if is_exclusively_test_issue_result and has_uncategorized_filter:
        return False
    if is_exclusively_test_issue_result or is_unknown_build_issue_result:
        issue_id = UNCATEGORIZED_STRING

    is_issue_filtered_out_result = is_issue_filtered_out(
        issue_id=issue_id, issue_version=issue_version, issue_filters=issue_filters
    )

    return is_issue_filtered_out_result


def should_increment_test_issue(
    issue_id: Optional[str],
    issue_version: Optional[int],
    incident_test_id: Optional[str],
) -> Tuple[str, int, bool]:
    is_exclusively_build_issue_result = is_exclusively_build_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )
    if is_exclusively_build_issue_result:
        return (UNCATEGORIZED_STRING, None, False)

    is_issue_from_test_result = is_issue_from_test(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )

    return (issue_id, issue_version, is_issue_from_test_result)


def should_increment_build_issue(
    *,
    issue_id: Optional[str],
    issue_version: Optional[int],
    incident_test_id: Optional[str],
    build_status: StatusValues,
) -> Tuple[str, int, bool]:
    is_exclusively_test_issue_result = is_exclusively_test_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )
    if is_exclusively_test_issue_result:
        return (UNCATEGORIZED_STRING, None, False)

    is_issue_from_build_result = is_issue_from_build(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )

    result = is_issue_from_build_result and is_status_failure(
        build_status, build_fail_status_list
    )

    return (issue_id, issue_version, result)


def to_int_or_default(value, default):
    if value:
        try:
            return int(value)
        except ValueError:
            return default
    return default


type FilterFields = Literal[
    "boot.status",
    "boot.duration",
    "test.status",
    "test.duration",
    "build.status",
    "duration",
    "origins",
    "config_name",
    "compiler",
    "architecture",
    "test.hardware",
    "test.path",
    "boot.path",
    "build.issue",
    "boot.issue",
    "test.issue",
    "boot.platform",
    "test.platform",
    "issue.culprit",
    "issue.categories",
    "issue.options",
]
type FilterHandlers = dict[FilterFields, Callable]


class InvalidComparisonOPError(
    Exception,
):
    pass


class FilterParams:
    """
    The param field form has two forms:
    - with a comparison operator ?filter_<field>_[<comparison_op>]=<value>
    - wit no comparison operator ?filter_<field>=<value>, the comparison operator `exact` will then be applied
    - Lists
        example: filter_category=cat1&filter_category=cat2
        if a list is received then the comparison operator `in` is applied
    """

    filter_reg = re.compile(r"^(.*)_\[(.*)\]$")
    filter_param_prefix = "filter_"
    comparison_op_type_idx = {"orm": 0, "raw": 1}

    comparison_ops = {
        "exact": ["exact", "="],
        "in": ["in", "IN"],
        "gt": ["gt", ">"],
        "gte": ["gte", ">="],
        "lt": ["lt", "<"],
        "lte": ["lte", "<="],
        "like": ["like", "LIKE"],
    }

    string_like_filters = ["boot.path", "test.path"]

    class ParsedFilter(TypedDict):
        field: str
        value: Any  # TODO: correctly type this field
        comparison_op: Literal["exact", "in", "gt", "gte", "lt", "lte", "like"]

    def __init__(self, data: Dict, process_body=False) -> None:
        self.filterTestDurationMin, self.filterTestDurationMax = None, None
        self.filterBootDurationMin, self.filterBootDurationMax = None, None
        self.filterBuildDurationMin, self.filterBuildDurationMax = None, None
        self.filterBootStatus = set()
        self.filterTestStatus = set()
        self.filterConfigs = set()
        self.filterCompiler = set()
        self.filterArchitecture = set()
        self.filterHardware = set()
        self.filterTestPath = ""
        self.filterBootPath = ""
        self.filterBuildStatus = set()
        self.filterIssues: dict[PossibleTabs, set[tuple[str, Optional[int]]]] = {
            "build": set(),
            "boot": set(),
            "test": set(),
        }
        self.filterPlatforms = {
            "boot": set(),
            "test": set(),
        }
        self.filter_labs: set[str] = set()

        self.filter_issue_culprits: set[PossibleIssueCulprits] = set()
        self.filter_origins: set[str] = set()
        self.filter_issue_categories: set[str] = set()
        self.filter_issue_options: set[IssueFilterOptions] = set()

        self.filter_build_origin: set[str] = set()
        self.filter_boot_origin: set[str] = set()
        self.filter_test_origin: set[str] = set()

        self.filter_handlers: FilterHandlers = {
            "boot.status": self._handle_boot_status,
            "boot.duration": self._handle_boot_duration,
            "test.status": self._handle_test_status,
            "test.duration": self._handle_test_duration,
            "build.status": self._handle_build_status,
            "build.duration": self._handle_build_duration,
            "origin": self._handle_origins,
            "config_name": self._handle_config_name,
            "compiler": self._handle_compiler,
            "architecture": self._handle_architecture,
            "test.hardware": self._handle_hardware,
            "test.lab": self._handle_labs,
            "test.path": self._handle_path,
            "boot.path": self._handle_path,
            "build.issue": self._handle_issues,
            "boot.issue": self._handle_issues,
            "test.issue": self._handle_issues,
            "boot.platform": self._handle_platforms,
            "test.platform": self._handle_platforms,
            "issue.culprit": self._handle_issue_culprits,
            "issue.categories": self._handle_issue_categories,
            "issue.options": self._handle_issue_options,
            "build.origin": self._handle_build_origin,
            "boot.origin": self._handle_boot_origin,
            "test.origin": self._handle_test_origin,
        }

        self.filters: List[FilterParams.ParsedFilter] = []
        if process_body:
            self.create_filters_from_body(data)
        else:
            self.create_filters_from_req(data)

        self._process_filters()

    def _handle_boot_status(self, current_filter: ParsedFilter) -> None:
        self.filterBootStatus.add(current_filter["value"])

    def _handle_boot_duration(self, current_filter: ParsedFilter) -> None:
        value = current_filter["value"]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterBootDurationMax = to_int_or_default(value, None)
        else:
            self.filterBootDurationMin = to_int_or_default(value, None)

    def _handle_test_status(self, current_filter: ParsedFilter) -> None:
        self.filterTestStatus.add(current_filter["value"])

    def _handle_test_duration(self, current_filter: ParsedFilter) -> None:
        value = current_filter["value"]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterTestDurationMax = to_int_or_default(value, None)
        else:
            self.filterTestDurationMin = to_int_or_default(value, None)

    def _handle_config_name(self, current_filter: ParsedFilter) -> None:
        self.filterConfigs.add(current_filter["value"])

    def _handle_compiler(self, current_filter: ParsedFilter) -> None:
        self.filterCompiler.add(current_filter["value"])

    def _handle_architecture(self, current_filter: ParsedFilter) -> None:
        self.filterArchitecture.add(current_filter["value"])

    def _handle_hardware(self, current_filter: ParsedFilter) -> None:
        self.filterHardware.add(current_filter["value"])

    def _handle_path(self, current_filter: ParsedFilter) -> None:
        if current_filter["field"] == "boot.path":
            self.filterBootPath = current_filter["value"]
        else:
            self.filterTestPath = current_filter["value"]

    def _handle_build_status(self, current_filter: ParsedFilter) -> None:
        self.filterBuildStatus.add(current_filter["value"])

    def _handle_build_duration(self, current_filter: ParsedFilter) -> None:
        value = current_filter["value"][0]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterBuildDurationMax = to_int_or_default(value, None)
        else:
            self.filterBuildDurationMin = to_int_or_default(value, None)

    def _handle_issues(self, current_filter: ParsedFilter) -> None:
        tab = current_filter["field"].split(".")[0]

        filter_value = current_filter["value"]
        if filter_value == UNCATEGORIZED_STRING:
            self.filterIssues[tab].add((UNCATEGORIZED_STRING, None))
        else:
            issue_id, issue_version = filter_value.rsplit(",", 1)
            issue_version = int(issue_version) if issue_version != "null" else None

            self.filterIssues[tab].add((issue_id, issue_version))

    def _handle_platforms(self, current_filter: ParsedFilter) -> None:
        tab = current_filter["field"].split(".")[0]
        self.filterPlatforms[tab].add(current_filter["value"])

    def _handle_labs(self, current_filter: ParsedFilter) -> None:
        self.filter_labs.add(current_filter["value"])

    def _handle_issue_culprits(self, current_filter: ParsedFilter) -> None:
        filter_value = current_filter["value"]
        if filter_value not in POSSIBLE_CULPRITS:
            log_message(
                f"Ignoring issue_culprit value not allowed for filters: {filter_value}"
            )
            return
        self.filter_issue_culprits.add(current_filter["value"])

    def _handle_origins(self, current_filter: ParsedFilter) -> None:
        self.filter_origins.add(current_filter["value"])

    def _handle_issue_categories(self, current_filter: ParsedFilter) -> None:
        self.filter_issue_categories.add(current_filter["value"])

    def _handle_issue_options(self, current_filter: ParsedFilter) -> None:
        filter_value = current_filter["value"]
        if filter_value not in ISSUE_FILTER_OPTIONS:
            log_message(f"Ignoring issue filter option not allowed: {filter_value}")
            return
        self.filter_issue_options.add(filter_value)

    def _handle_build_origin(self, current_filter: ParsedFilter) -> None:
        self.filter_build_origin.add(current_filter["value"])

    def _handle_boot_origin(self, current_filter: ParsedFilter) -> None:
        self.filter_boot_origin.add(current_filter["value"])

    def _handle_test_origin(self, current_filter: ParsedFilter) -> None:
        self.filter_test_origin.add(current_filter["value"])

    def _process_filters(self):
        try:
            for current_filter in self.filters:
                field = current_filter["field"]
                # Delegate to the appropriate handler based on the field
                if field in self.filter_handlers:
                    self.filter_handlers[field](current_filter)
        except InvalidComparisonOPError as e:
            return HttpResponseBadRequest(get_error_body_response(str(e)))

    def create_filters_from_body(self, body: Dict):
        filters = body.get("filter", {})
        for k in filters.keys():
            if not k.startswith(self.filter_param_prefix):
                continue
            # HACK: Flake8 will always bug with (): so we define a variable here
            filter_param_prefix_length = len(self.filter_param_prefix)
            filter_term = k[filter_param_prefix_length:]

            # filter as list
            filter_data = filters.get(k)

            match = self.filter_reg.match(filter_term)

            if match:
                field = match.group(1)
                comparison_op = match.group(2)
                self.add_filter(field, filter_data[0], comparison_op)
                continue

            if type(filter_data) is list and len(filter_data) > 0:
                field = filter_term
                values = filter_data

                for value in values:
                    self.add_filter(field, value, "in")
                continue

            if filter_term in self.string_like_filters:
                self.add_filter(filter_term, filter_data, "like")
                continue

            self.add_filter(filter_term, filter_data, "exact")

    def create_filters_from_req(self, request: HttpRequest) -> None:
        for k in request.GET.keys():
            if not k.startswith(self.filter_param_prefix):
                continue
            # HACK: Flake8 will always bug with (): so we define a variable here
            filter_param_prefix_length = len(self.filter_param_prefix)
            filter_term = k[filter_param_prefix_length:]

            # filter as list
            if len(request.GET.getlist(k)) > 1:
                field = filter_term
                values = request.GET.getlist(k)

                for value in values:
                    self.add_filter(field, value, "in")
                continue

            if filter_term in self.string_like_filters:
                self.add_filter(filter_term, request.GET.get(k), "like")
                continue

            match = self.filter_reg.match(filter_term)
            if match:
                field = match.group(1)
                comparison_op = match.group(2)
                self.add_filter(field, request.GET.get(k), comparison_op)
                continue

            self.add_filter(filter_term, request.GET.get(k), "exact")

    def add_filter(self, field: str, value: Any, comparison_op: str) -> None:
        self.validate_comparison_op(comparison_op)
        self.filters.append(
            {"field": field, "value": value, "comparison_op": comparison_op}
        )

    def validate_comparison_op(self, op):
        if op not in self.comparison_ops.keys():
            raise InvalidComparisonOPError(
                f"Filter with invalid comparison operator `{op}` found`"
            )

    def get_comparison_op(self, filter, op_type="orm"):
        idx = self.comparison_op_type_idx[op_type]
        return self.comparison_ops[filter["comparison_op"]][idx]

    def get_grouped_filters(self):
        grouped_filters = {}

        for f in self.filters:
            field = f["field"]
            value = f["value"]
            if field not in grouped_filters:
                grouped_filters[field] = f
            elif type(grouped_filters[field]["value"]) is str:
                grouped_filters[field]["value"] = [
                    grouped_filters[field]["value"],
                    value,
                ]
            else:
                grouped_filters[field]["value"].append(value)

        return grouped_filters

    def is_build_filtered_out(
        self,
        *,
        duration: Optional[int],
        build_status: StatusValues,
        issue_id: Optional[str],
        issue_version: Optional[int],
        incident_test_id: Optional[str],
        build_origin: Optional[str] = None,
    ) -> bool:
        return (
            (
                len(self.filterBuildStatus) > 0
                and (build_status.upper() not in self.filterBuildStatus)
            )
            or (
                (
                    self.filterBuildDurationMax is not None
                    or self.filterBuildDurationMin is not None
                )
                and duration is None
            )
            or (
                self.filterBuildDurationMax is not None
                and (to_int_or_default(duration, 0) > self.filterBuildDurationMax)
            )
            or (
                self.filterBuildDurationMin is not None
                and (to_int_or_default(duration, 0) < self.filterBuildDurationMin)
            )
            or (
                len(self.filter_build_origin) > 0
                and (build_origin not in self.filter_build_origin)
            )
            or (
                should_filter_build_issue(
                    issue_filters=self.filterIssues["build"],
                    issue_id=issue_id,
                    issue_version=issue_version,
                    incident_test_id=incident_test_id,
                    build_status=build_status,
                )
            )
        )

    def is_record_filtered_out(
        self,
        *,
        hardwares: Optional[List[str]] = None,
        architecture: Optional[str],
        compiler: Optional[str],
        config_name: Optional[str],
        lab: Optional[str] = UNKNOWN_STRING,
    ) -> bool:
        hardware_compatibles = [UNKNOWN_STRING]
        record_architecture = UNKNOWN_STRING
        record_compiler = UNKNOWN_STRING
        record_config_name = UNKNOWN_STRING
        record_lab = UNKNOWN_STRING if lab is None else lab

        if hardwares is not None:
            hardware_compatibles = hardwares
        if architecture is not None:
            record_architecture = architecture
        if compiler is not None:
            record_compiler = compiler
        if config_name is not None:
            record_config_name = config_name

        if (
            (
                len(self.filterHardware) > 0
                and (not self.filterHardware.intersection(hardware_compatibles))
            )
            or (
                len(self.filterArchitecture) > 0
                and (record_architecture not in self.filterArchitecture)
            )
            or (
                len(self.filterCompiler) > 0
                and (record_compiler not in self.filterCompiler)
            )
            or (
                len(self.filterConfigs) > 0
                and (record_config_name not in self.filterConfigs)
            )
            or (len(self.filter_labs) > 0 and (record_lab not in self.filter_labs))
        ):
            return True

        return False

    def is_boot_filtered_out(
        self,
        *,
        path: Optional[str],
        status: Optional[str],
        duration: Optional[int],
        issue_id: Optional[str] = None,
        issue_version: Optional[int] = None,
        incident_test_id: Optional[str] = "incident_test_id",
        platform: Optional[str] = None,
        origin: Optional[str] = None,
    ) -> bool:
        if (
            (self.filterBootPath != "" and (self.filterBootPath not in path))
            or (
                len(self.filterBootStatus) > 0 and (status not in self.filterBootStatus)
            )
            or (
                (
                    self.filterBootDurationMax is not None
                    or self.filterBootDurationMin is not None
                )
                and duration is None
            )
            or (
                self.filterBootDurationMax is not None
                and (to_int_or_default(duration, 0) > self.filterBootDurationMax)
            )
            or (
                self.filterBootDurationMin is not None
                and (to_int_or_default(duration, 0) < self.filterBootDurationMin)
            )
            or should_filter_test_issue(
                issue_filters=self.filterIssues["boot"],
                issue_id=issue_id,
                issue_version=issue_version,
                incident_test_id=incident_test_id,
            )
            or (
                len(self.filterPlatforms["boot"]) > 0
                and (platform not in self.filterPlatforms["boot"])
            )
            or (
                len(self.filter_boot_origin) > 0
                and (origin not in self.filter_boot_origin)
            )
        ):
            return True

        return False

    def is_test_filtered_out(
        self,
        *,
        path: Optional[str],
        status: Optional[str],
        duration: Optional[int],
        issue_id: Optional[str] = None,
        issue_version: Optional[int] = None,
        incident_test_id: Optional[str] = "incident_test_id",
        platform: Optional[str] = None,
        origin: Optional[str] = None,
    ) -> bool:
        if (
            (self.filterTestPath != "" and (self.filterTestPath not in path))
            or (
                len(self.filterTestStatus) > 0 and (status not in self.filterTestStatus)
            )
            or (
                (
                    self.filterTestDurationMax is not None
                    or self.filterTestDurationMin is not None
                )
                and duration is None
            )
            or (
                self.filterTestDurationMax is not None
                and (to_int_or_default(duration, 0) > self.filterTestDurationMax)
            )
            or (
                self.filterTestDurationMin is not None
                and (to_int_or_default(duration, 0) < self.filterTestDurationMin)
            )
            or should_filter_test_issue(
                issue_filters=self.filterIssues["test"],
                issue_id=issue_id,
                issue_version=issue_version,
                incident_test_id=incident_test_id,
            )
            or (
                len(self.filterPlatforms["test"]) > 0
                and (platform not in self.filterPlatforms["test"])
            )
            or (
                len(self.filter_test_origin) > 0
                and (origin not in self.filter_test_origin)
            )
        ):
            return True

        return False
