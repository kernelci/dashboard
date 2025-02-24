from abc import ABC
from typing import Any
from urllib.parse import urljoin, urlencode


class BaseClient(ABC):
    base_url = "http://localhost:8000/"

    def get_endpoint(self, *, path: str, query: dict[str, Any] | None = None) -> str:
        url = urljoin(self.base_url, path)
        if query is not None:
            # When a value has None value, the urlencode function change it into a string.
            # This logic remove None values from the query dict
            query = {k: v for k, v in query.items() if v is not None}
            query_encoded = urlencode(query)
            url = f"{url}?{query_encoded}"
        return url
