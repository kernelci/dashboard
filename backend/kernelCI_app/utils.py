import json
from typing import Union, TypedDict, List, Optional, Dict
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponseBadRequest
import re

DEFAULT_QUERY_TIME_INTERVAL = {"days": 7}
UNKNOWN_STRING = "Unknown"
NULL_STRINGS = set(["null", UNKNOWN_STRING, "NULL"])


class IncidentInfo(TypedDict):
    incidentsCount: int


class Issue(TypedDict):
    id: str
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: IncidentInfo


def create_issue(
    *, issue_id: str, issue_comment: Optional[str], issue_report_url: Optional[str]
) -> Issue:
    return {
        "id": issue_id,
        "comment": issue_comment,
        "report_url": issue_report_url,
        "incidents_info": {"incidentsCount": 1},
    }


def convert_issues_dict_to_list(issues_dict: Dict[str, Issue]) -> List[Issue]:
    return list(issues_dict.values())


def toIntOrDefault(value, default):
    try:
        return int(value)
    except ValueError:
        return default


def extract_platform(misc_environment: Union[str, dict, None]):
    parsedEnvMisc = None
    if isinstance(misc_environment, dict):
        parsedEnvMisc = misc_environment
    elif misc_environment is None:
        return "unknown"
    else:
        parsedEnvMisc = json.loads(misc_environment)
    platform = parsedEnvMisc.get("platform")
    if platform:
        return platform
    return "unknown"


# TODO misc is not stable and should be used as a POC only
def extract_error_message(misc: Union[str, dict, None]):
    parsedEnv = None
    if misc is None:
        return "unknown error"
    elif isinstance(misc, dict):
        parsedEnv = misc
    else:
        parsedEnv = json.loads(misc)
    error_message = parsedEnv.get("error_msg")
    if error_message:
        return error_message
    return "unknown error"


def getQueryTimeInterval(**kwargs):
    if not kwargs:
        return timezone.now() - timedelta(**DEFAULT_QUERY_TIME_INTERVAL)
    return timezone.now() - timedelta(**kwargs)


def getErrorResponseBody(reason: str):
    return json.dumps({"error": True, "reason": reason})


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

    def __init__(self, data: Dict, process_body=False):
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
        self.filterIssues = {
            "build": set(),
            "boot": set(),
            "test": set()
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
        }

        self.filters = []
        if process_body:
            self.create_filters_from_body(data)
        else:
            self.create_filters_from_req(data)

        self._processFilters()

    def _handle_boot_status(self, current_filter: Dict):
        self.filterBootStatus.add(current_filter["value"])

    def _handle_boot_duration(self, current_filter: Dict):
        value = current_filter["value"]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterBootDurationMax = toIntOrDefault(value, None)
        else:
            self.filterBootDurationMin = toIntOrDefault(value, None)

    def _handle_test_status(self, current_filter: Dict):
        self.filterTestStatus.add(current_filter["value"])

    def _handle_test_duration(self, current_filter: Dict):
        value = current_filter["value"]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterTestDurationMax = toIntOrDefault(value, None)
        else:
            self.filterTestDurationMin = toIntOrDefault(value, None)

    def _handle_config_name(self, current_filter: Dict):
        self.filterConfigs.add(current_filter["value"])

    def _handle_compiler(self, current_filter: Dict):
        self.filterCompiler.add(current_filter["value"])

    def _handle_architecture(self, current_filter: Dict):
        self.filterArchitecture.add(current_filter["value"])

    def _handle_hardware(self, current_filter: Dict):
        self.filterHardware.add(current_filter["value"])

    def _handle_path(self, current_filter: Dict):
        if current_filter["field"] == "boot.path":
            self.filterBootPath = current_filter["value"]
        else:
            self.filterTestPath = current_filter["value"]

    def _handle_build_valid(self, current_filter: Dict):
        self.filterBuildValid.add(current_filter["value"])

    def _handle_build_duration(self, current_filter: Dict):
        value = current_filter["value"][0]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterBuildDurationMax = toIntOrDefault(value, None)
        else:
            self.filterBuildDurationMin = toIntOrDefault(value, None)

    def _handle_issues(self, current_filter):
        tab = current_filter["field"].split('.')[0]
        self.filterIssues[tab].add(current_filter["value"])

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

    def add_filter(self, field, value, comparison_op):
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
            value = f['value']
            if field not in grouped_filters:
                grouped_filters[field] = f
            elif type(grouped_filters[field]['value']) is str:
                grouped_filters[field]['value'] = [grouped_filters[field]['value'], value]
            else:
                grouped_filters[field]['value'].append(value)

        return grouped_filters
