import json
from django.utils import timezone
from datetime import timedelta
import re

DEFAULT_QUERY_TIME_INTERVAL = {'days': 7}


def getQueryTimeInterval(**kwargs):
    if not kwargs:
        return timezone.now() - timedelta(**DEFAULT_QUERY_TIME_INTERVAL)
    return timezone.now() - timedelta(**kwargs)


def getErrorResponseBody(reason):
    return json.dumps({"error": True, "reason": reason})


class InvalidComparisonOP(Exception,):
    pass


class FilterParams():
    '''
    The param field form has two forms:
    - with a comparison operator ?filter_<field>_[<comparison_op>]=<value>
    - wit no comparison operator ?filter_<field>=<value>, the comparison operator `exact` will then be applied
    - Lists
        example: filter_category=cat1&ffilter_category=cat2
        if a list is received then the comparison operator `in` is applied
    '''
    filter_reg = re.compile(r"^(.*)_\[(.*)\]$")
    filter_param_prefix = 'filter_'
    comparison_ops = {
        'exact': 'exact',
        'in': 'in',
        'gt': 'gt',
        'gte': 'gte',
        'lt': 'lt',
        'lte': 'lte',
    }

    def __init__(self, request):
        self.filters = []
        self.create_filters_from_req(request)

    def create_filters_from_req(self, request):
        for k in request.GET.keys():
            if not k.startswith(self.filter_param_prefix):
                continue
            filter_term = k[len(self.filter_param_prefix):]

            # filter as list
            if len(request.GET.getlist(k)) > 1:
                field = filter_term
                value = request.GET.getlist(k)
                self.add_filter(field, value, 'in')
                continue

            match = self.filter_reg.match(filter_term)
            if match:
                field = match.group(1)
                comparison_op = match.group(2)
                self.add_filter(field, request.GET.get(k), comparison_op)
                continue

            self.add_filter(filter_term, request.GET.get(k), 'exact')

    def add_filter(self, field, value, comparison_op):
        self.validate_comparison_op(comparison_op)
        self.filters.append({'field': field, 'value': value, 'comparison_op': comparison_op})

    def validate_comparison_op(self, op):
        if op not in self.comparison_ops.values():
            raise InvalidComparisonOP(f'Filter with invalid comparison operator `{op}` found`')
