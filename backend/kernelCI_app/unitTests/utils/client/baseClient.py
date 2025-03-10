from abc import ABC
from typing import Any, Optional
from urllib.parse import urljoin, urlencode
from kernelCI_app.helpers.filters import FilterFields


class BaseClient(ABC):
    base_url = "http://localhost:8000/"

    def get_endpoint(
        self,
        *,
        path: str,
        query: Optional[dict[str, Any]] = None,
        filters: Optional[dict[FilterFields, Any]] = None,
    ) -> str:
        url = urljoin(self.base_url, path)

        query_string = ""
        if query is not None:
            if filters:
                query = self.join_query(query=query, filters=filters)

            # When a value has None value, the urlencode function change it into a string.
            # This logic remove None values from the query dict
            query = {k: v for k, v in query.items() if v is not None}
            query_string = f"?{urlencode(query)}"
        elif filters is not None:
            query_string = f"?{urlencode(self.get_filters(filters=filters))}"
        url = f"{url}{query_string}"
        return url

    def get_filters(self, *, filters: dict[FilterFields, Any]) -> dict[str, Any]:
        prefix = "filter_"
        return {f"{prefix}{key}": value for key, value in filters.items()}

    def join_query(
        self, *, query: dict[str, Any], filters: dict[FilterFields, Any]
    ) -> dict[str, Any]:
        filters = self.get_filters(filters=filters)
        return dict(query, **filters)
