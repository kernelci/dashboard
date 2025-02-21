from abc import ABC
from typing import Any
from urllib.parse import urljoin, urlencode
from kernelCI_app.helpers.filters import FilterFields


class BaseClient(ABC):
    base_url = "http://localhost:8000/"

    def get_endpoint(
        self,
        *,
        path: str,
        query: dict[str, Any] | None = None,
        filters: dict[FilterFields, Any] | None = None,
    ) -> str:
        url = urljoin(self.base_url, path)

        query_string = ""
        if query is not None and filters is not None:
            query_string = (
                f"?{urlencode(self.join_query(query=query, filters=filters))}"
            )
        elif query is not None:
            query_string = f"?{urlencode(query)}"
        elif filters is not None:
            query_string = f"?{urlencode(self.get_filters(filters=filters))}"
        url = f"{url}{query_string}"
        return url

    def get_filters(*, filters: dict[FilterFields, Any]) -> dict[str, Any]:
        prefix = "filter_"
        return {f"{prefix}{key}": value for key, value in filters.items()}

    def join_query(
        self, *, query: dict[str, Any], filters: dict[FilterFields, Any]
    ) -> dict[str, Any]:
        filters = self.get_filters(filters=filters)
        return dict(query, **filters)
