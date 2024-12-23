from typing import Optional, Dict, List, TypedDict, Literal, Any
from django.http import HttpResponseBadRequest
import re
from kernelCI_app.utils import getErrorResponseBody

UNKNOWN_STRING = "Unknown"
NULL_STRINGS = set(["null", UNKNOWN_STRING, "NULL"])


def is_build_invalid(build_valid: Optional[bool]) -> bool:
    return build_valid is None or build_valid is False


def is_known_issue(issue_id: Optional[str]) -> bool:
    return issue_id is not None and issue_id is not UNKNOWN_STRING


def is_issue_from_test(incident_test_id: Optional[str], is_known_issue: bool) -> bool:
    return incident_test_id is not None or not is_known_issue


def is_issue_filtered_out(issue_id: Optional[str], issue_filters: set) -> bool:
    return issue_id not in issue_filters


def should_filter_test_issue(
    issue_filters: set, issue_id: Optional[str], incident_test_id: Optional[str]
) -> bool:
    has_issue_filter = len(issue_filters) > 0

    is_known_issue_result = is_known_issue(issue_id)
    is_issue_from_tests_result = is_issue_from_test(
        incident_test_id, is_known_issue_result
    )

    is_issue_filtered_out_result = is_issue_filtered_out(issue_id, issue_filters)

    return (
        has_issue_filter and is_issue_from_tests_result and is_issue_filtered_out_result
    )


def should_increment_test_issue(
    issue_id: Optional[str], incident_test_id: Optional[str]
) -> bool:
    is_known_issue_result = is_known_issue(issue_id=issue_id)
    is_exclusively_build_issue = is_known_issue_result and incident_test_id is None
    if is_exclusively_build_issue:
        issue_id = UNKNOWN_STRING

    is_unknown_issue = issue_id is UNKNOWN_STRING
    is_known_test_issue = incident_test_id is not None
    is_issue_from_test = is_known_test_issue or is_unknown_issue

    return is_issue_from_test


def toIntOrDefault(value, default):
    try:
        return int(value)
    except ValueError:
        return default


class InvalidComparisonOP(
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
        self.filterBuildValid = set()
        self.filterIssues = {"build": set(), "boot": set(), "test": set()}
        self.filterPlatforms = {
            "build": set(),
            "boot": set(),
            "test": set(),
        }

        self.filter_handlers = {
            "boot.status": self._handle_boot_status,
            "boot.duration": self._handle_boot_duration,
            "test.status": self._handle_test_status,
            "test.duration": self._handle_test_duration,
            "duration": self._handle_build_duration,
            "config_name": self._handle_config_name,
            "compiler": self._handle_compiler,
            "architecture": self._handle_architecture,
            "valid": self._handle_build_valid,
            "test.hardware": self._handle_hardware,
            "test.path": self._handle_path,
            "boot.path": self._handle_path,
            "build.issue": self._handle_issues,
            "boot.issue": self._handle_issues,
            "test.issue": self._handle_issues,
            "build.platform": self._handle_platforms,
            "boot.platform": self._handle_platforms,
            "test.platform": self._handle_platforms,
        }

        self.filters: List[FilterParams.ParsedFilter] = []
        if process_body:
            self.create_filters_from_body(data)
        else:
            self.create_filters_from_req(data)

        self._processFilters()

    def _handle_boot_status(self, current_filter: ParsedFilter) -> None:
        self.filterBootStatus.add(current_filter["value"])

    def _handle_boot_duration(self, current_filter: ParsedFilter) -> None:
        value = current_filter["value"]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterBootDurationMax = toIntOrDefault(value, None)
        else:
            self.filterBootDurationMin = toIntOrDefault(value, None)

    def _handle_test_status(self, current_filter: ParsedFilter) -> None:
        self.filterTestStatus.add(current_filter["value"])

    def _handle_test_duration(self, current_filter: ParsedFilter) -> None:
        value = current_filter["value"]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterTestDurationMax = toIntOrDefault(value, None)
        else:
            self.filterTestDurationMin = toIntOrDefault(value, None)

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

    def _handle_build_valid(self, current_filter: ParsedFilter) -> None:
        self.filterBuildValid.add(current_filter["value"])

    def _handle_build_duration(self, current_filter: ParsedFilter) -> None:
        value = current_filter["value"][0]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterBuildDurationMax = toIntOrDefault(value, None)
        else:
            self.filterBuildDurationMin = toIntOrDefault(value, None)

    def _handle_issues(self, current_filter: ParsedFilter) -> None:
        tab = current_filter["field"].split(".")[0]
        self.filterIssues[tab].add(current_filter["value"])

    def _handle_platforms(self, current_filter: ParsedFilter) -> None:
        tab = current_filter["field"].split(".")[0]
        self.filterPlatforms[tab].add(current_filter["value"])

    def _processFilters(self):
        try:
            for current_filter in self.filters:
                field = current_filter["field"]
                # Delegate to the appropriate handler based on the field
                if field in self.filter_handlers:
                    self.filter_handlers[field](current_filter)
        except InvalidComparisonOP as e:
            return HttpResponseBadRequest(getErrorResponseBody(str(e)))

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

    def create_filters_from_req(self, request):
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
            raise InvalidComparisonOP(
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
        valid: Optional[bool],
        issue_id: Optional[str],
        platform: Optional[str] = None,
    ) -> bool:
        return (
            (
                len(self.filterBuildValid) > 0
                and (str(valid).lower() not in self.filterBuildValid)
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
                and (toIntOrDefault(duration, 0) > self.filterBuildDurationMax)
            )
            or (
                self.filterBuildDurationMin is not None
                and (toIntOrDefault(duration, 0) < self.filterBuildDurationMin)
            )
            or (
                len(self.filterIssues["build"]) > 0
                and (issue_id not in self.filterIssues["build"] or valid is True)
            )
            or (
                len(self.filterPlatforms["build"]) > 0
                and (platform not in self.filterPlatforms["build"])
            )
        )

    def is_record_filtered_out(
        self,
        *,
        hardwares: Optional[List[str]] = None,
        architecture: Optional[str],
        compiler: Optional[str],
        config_name: Optional[str],
    ) -> bool:
        hardware_compatibles = [UNKNOWN_STRING]
        record_architecture = UNKNOWN_STRING
        record_compiler = UNKNOWN_STRING
        record_config_name = UNKNOWN_STRING

        if hardwares is not None:
            hardware_compatibles = hardwares
        if architecture is not None:
            record_architecture = architecture
        if compile is not None:
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
        incident_test_id: Optional[str] = "incident_test_id",
        platform: Optional[str] = None,
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
                and (toIntOrDefault(duration, 0) > self.filterBootDurationMax)
            )
            or (
                self.filterBootDurationMin is not None
                and (toIntOrDefault(duration, 0) < self.filterBootDurationMin)
            )
            or should_filter_test_issue(
                self.filterIssues["boot"], issue_id, incident_test_id
            )
            or (
                len(self.filterPlatforms["boot"]) > 0
                and (platform not in self.filterPlatforms["boot"])
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
        incident_test_id: Optional[str] = "incident_test_id",
        platform: Optional[str] = None,
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
                and (toIntOrDefault(duration, 0) > self.filterTestDurationMax)
            )
            or (
                self.filterTestDurationMin is not None
                and (toIntOrDefault(duration, 0) < self.filterTestDurationMin)
            )
            or should_filter_test_issue(
                self.filterIssues["test"], issue_id, incident_test_id
            )
            or (
                len(self.filterPlatforms["test"]) > 0
                and (platform not in self.filterPlatforms["test"])
            )
        ):
            return True

        return False
