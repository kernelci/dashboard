from abc import ABC
from typing import Any, Optional
from urllib.parse import urljoin, urlencode
from kernelCI_app.helpers.filters import FilterFields
import os


class BaseClient(ABC):
    base_url = os.environ.get("TEST_BASE_URL", "http://localhost:8000/")

    def get_endpoint(
        self,
        *,
        path: str,
        query: Optional[dict[str, Any]] = None,
        filters: Optional[dict[FilterFields, Any]] = None,
    ) -> str:
        url = urljoin(self.base_url, path)

        query_string = ""
        string_parts = []

        if query is not None:
            # When a value has None value, the urlencode function change it into a string.
            # This logic remove None values from the query dict
            query = {k: v for k, v in query.items() if v is not None}
            string_parts.append(urlencode(query))
        if filters is not None:
            filters = {k: v for k, v in filters.items() if v is not None}
            mapped_filters = self.get_filters(filters=filters)
            string_parts.append(urlencode(mapped_filters, doseq=True))

        query_string = f"?{"&".join(string_parts)}" if string_parts else ""

        url = f"{url}{query_string}"
        return url

    def get_filters(self, *, filters: dict[FilterFields, Any]) -> dict[str, Any]:
        prefix = "filter_"
        return {f"{prefix}{key}": value for key, value in filters.items()}
