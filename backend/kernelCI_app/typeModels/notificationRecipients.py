import os
from typing import Annotated, Optional

import yaml
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, ValidationError

DEFAULT_FILE = "default.yaml"
HARDWARE_SUFFIX = "_hardware.yaml"


def _as_list(value):
    return [value] if isinstance(value, str) else value


type StrList = Annotated[list[str], BeforeValidator(_as_list), Field(min_length=1)]


class RecipientEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recipients: StrList
    issues: Optional[StrList] = None
    branch: Optional[StrList] = None
    architecture: Optional[StrList] = None
    config_name: Optional[StrList] = None
    compiler: Optional[StrList] = None

    @property
    def scope(self) -> dict[str, list[str]]:
        return self.model_dump(exclude={"recipients"}, exclude_none=True)


class RecipientDefault(BaseModel):
    model_config = ConfigDict(extra="forbid")

    to: str


class RecipientFileError(ValueError):
    def __init__(self, file: str, message: str, *, entry=None, key=None):
        where = [file]
        if entry is not None:
            where.append(f"entry {entry}")
        if key is not None:
            where.append(f"key '{key}'")
        super().__init__(f"{': '.join(where)}: {message}")


def _read_yaml(path: str):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as exc:
        raise RecipientFileError(path, str(exc)) from exc


def _yaml_files(directory: str) -> list[str]:
    return sorted(f for f in os.listdir(directory) if f.endswith((".yaml", ".yml")))


def _tree_urls(subscriptions_directory: str) -> dict[str, str]:
    """Maps each tree key in the subscription files to its url"""
    tree_urls: dict[str, str] = {}
    files_by_url: dict[str, str] = {}
    for filename in _yaml_files(subscriptions_directory):
        if filename.endswith(HARDWARE_SUFFIX):
            continue
        path = os.path.join(subscriptions_directory, filename)
        for tree_key, values in (_read_yaml(path) or {}).items():
            url = values.get("url")
            if url in files_by_url:
                raise RecipientFileError(
                    path,
                    f"url {url} is also used by {files_by_url[url]}",
                    key="url",
                )
            files_by_url[url] = filename
            tree_urls[tree_key] = url
    return tree_urls


def _parse_entry(path, index, raw, *, allowed_keys, allowed_issues) -> RecipientEntry:
    if not isinstance(raw, dict):
        raise RecipientFileError(path, "entry must be a mapping", entry=index)
    for key in raw:
        if key != "recipients" and key not in allowed_keys:
            raise RecipientFileError(path, "key not allowed", entry=index, key=key)
    try:
        entry = RecipientEntry.model_validate(raw)
    except ValidationError as exc:
        error = exc.errors()[0]
        key = error["loc"][0] if error["loc"] else None
        raise RecipientFileError(path, error["msg"], entry=index, key=key) from exc
    for issue in entry.issues or []:
        if issue not in allowed_issues:
            raise RecipientFileError(
                path, f"issue '{issue}' not allowed", entry=index, key="issues"
            )
    return entry


def load_recipient_files(
    directory: str,
    *,
    allowed_keys: set[str],
    allowed_issues: set[str],
    subscriptions_directory: Optional[str] = None,
) -> dict[str, list[RecipientEntry]]:
    """Loads and validates every recipient file in `directory`.

    Each top-level key must be a tree key from the subscription files, which
    default to the `subscriptions` folder next to `directory`.

    Returns the entries keyed by the tree's git url.
    Raises RecipientFileError naming the file, entry index, and key.
    """
    if subscriptions_directory is None:
        subscriptions_directory = os.path.join(
            os.path.dirname(os.path.normpath(directory)), "subscriptions"
        )
    tree_urls = _tree_urls(subscriptions_directory)

    entries_by_url: dict[str, list[RecipientEntry]] = {}
    for filename in _yaml_files(directory):
        if filename == DEFAULT_FILE:
            continue
        path = os.path.join(directory, filename)
        if filename.endswith(HARDWARE_SUFFIX):
            raise RecipientFileError(path, "hardware files are not allowed")
        data = _read_yaml(path)
        if not isinstance(data, dict):
            raise RecipientFileError(path, "file must map tree keys to entries")
        for tree_key, raw_entries in data.items():
            if tree_key not in tree_urls:
                raise RecipientFileError(
                    path, f"unknown tree '{tree_key}'", key=tree_key
                )
            if not isinstance(raw_entries, list):
                raise RecipientFileError(
                    path, "tree must hold a list of entries", key=tree_key
                )
            entries_by_url.setdefault(tree_urls[tree_key], []).extend(
                _parse_entry(
                    path,
                    index,
                    raw,
                    allowed_keys=allowed_keys,
                    allowed_issues=allowed_issues,
                )
                for index, raw in enumerate(raw_entries)
            )
    return entries_by_url


def load_recipient_default(directory: str) -> RecipientDefault:
    path = os.path.join(directory, DEFAULT_FILE)
    try:
        return RecipientDefault.model_validate(_read_yaml(path))
    except ValidationError as exc:
        error = exc.errors()[0]
        key = error["loc"][0] if error["loc"] else None
        raise RecipientFileError(path, error["msg"], key=key) from exc
