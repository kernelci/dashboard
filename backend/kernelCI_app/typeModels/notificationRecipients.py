import os
from typing import Annotated, Optional

import yaml
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PrivateAttr,
    ValidationError,
)

from kernelCI_app.constants.general import DEFAULT_ORIGIN

DEFAULT_FILE = "default.yaml"
HARDWARE_SUFFIX = "_hardware.yaml"
NEW_ISSUES_FOLDER = "notifications/new_issues"
NEW_ISSUE_KEYS = {"issues", "branch", "origin", "platform"}
NEW_ISSUE_KINDS = {"build", "boot", "test"}


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
    platform: Optional[StrList] = None
    origin: Optional[StrList] = None
    _tree_url: Optional[str] = PrivateAttr(default=None)
    _hardware_platform: Optional[str] = PrivateAttr(default=None)
    _source_file: str = PrivateAttr(default="")

    @property
    def scope(self) -> dict[str, list[str]]:
        return self.model_dump(exclude={"recipients"}, exclude_none=True)

    @property
    def tree_url(self) -> Optional[str]:
        return self._tree_url

    @property
    def hardware_platform(self) -> Optional[str]:
        return self._hardware_platform

    @property
    def source_file(self) -> str:
        return self._source_file


class RecipientDefault(BaseModel):
    model_config = ConfigDict(extra="forbid")

    to: str


class NewIssuesDefault(RecipientDefault):
    issues: StrList


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


def _subscriptions_directory(directory: str) -> str:
    return os.path.join(os.path.dirname(os.path.normpath(directory)), "subscriptions")


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


def _hardware_origins(subscriptions_directory: str) -> dict[str, str]:
    """Maps each platform key in *_hardware.yaml to its origin (maestro if omitted)."""
    origins: dict[str, str] = {}
    for filename in _yaml_files(subscriptions_directory):
        if not filename.endswith(HARDWARE_SUFFIX):
            continue
        path = os.path.join(subscriptions_directory, filename)
        for platform, values in (_read_yaml(path) or {}).items():
            origin = DEFAULT_ORIGIN
            if isinstance(values, dict) and values.get("origin"):
                origin = values["origin"]
            origins.setdefault(platform, origin)
    return origins


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


def _append_key_entries(
    entries: list[RecipientEntry],
    *,
    path: str,
    filename: str,
    key: str,
    raw_entries,
    is_hardware: bool,
    tree_urls: dict[str, str],
    hardware_origins: dict[str, str],
    allowed_keys: set[str],
    allowed_issues: set[str],
) -> None:
    if is_hardware and key not in hardware_origins:
        raise RecipientFileError(path, f"unknown platform '{key}'", key=key)
    if not is_hardware and key not in tree_urls:
        raise RecipientFileError(path, f"unknown tree '{key}'", key=key)
    if not isinstance(raw_entries, list):
        raise RecipientFileError(path, "tree must hold a list of entries", key=key)
    for index, raw in enumerate(raw_entries):
        entry = _parse_entry(
            path,
            index,
            raw,
            allowed_keys=allowed_keys,
            allowed_issues=allowed_issues,
        )
        entry._source_file = filename
        if is_hardware:
            entry._hardware_platform = key
            if entry.origin is None:
                entry.origin = [hardware_origins[key]]
        else:
            entry._tree_url = tree_urls[key]
        entries.append(entry)


def _collect_entries(
    directory: str,
    *,
    allowed_keys: set[str],
    allowed_issues: set[str],
    allow_hardware: bool,
    subscriptions_directory: str,
) -> list[RecipientEntry]:
    tree_urls = _tree_urls(subscriptions_directory)
    hardware_origins = (
        _hardware_origins(subscriptions_directory) if allow_hardware else {}
    )
    entries: list[RecipientEntry] = []
    for filename in _yaml_files(directory):
        if filename == DEFAULT_FILE:
            continue
        path = os.path.join(directory, filename)
        is_hardware = filename.endswith(HARDWARE_SUFFIX)
        if is_hardware and not allow_hardware:
            raise RecipientFileError(path, "hardware files are not allowed")
        data = _read_yaml(path)
        if not isinstance(data, dict):
            raise RecipientFileError(path, "file must map tree keys to entries")
        for key, raw_entries in data.items():
            _append_key_entries(
                entries,
                path=path,
                filename=filename,
                key=key,
                raw_entries=raw_entries,
                is_hardware=is_hardware,
                tree_urls=tree_urls,
                hardware_origins=hardware_origins,
                allowed_keys=allowed_keys,
                allowed_issues=allowed_issues,
            )
    return entries


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
        subscriptions_directory = _subscriptions_directory(directory)
    entries_by_url: dict[str, list[RecipientEntry]] = {}
    for entry in _collect_entries(
        directory,
        allowed_keys=allowed_keys,
        allowed_issues=allowed_issues,
        allow_hardware=False,
        subscriptions_directory=subscriptions_directory,
    ):
        entries_by_url.setdefault(entry.tree_url, []).append(entry)
    return entries_by_url


def load_recipient_default(directory: str) -> RecipientDefault:
    path = os.path.join(directory, DEFAULT_FILE)
    try:
        return RecipientDefault.model_validate(_read_yaml(path))
    except ValidationError as exc:
        error = exc.errors()[0]
        key = error["loc"][0] if error["loc"] else None
        raise RecipientFileError(path, error["msg"], key=key) from exc


def load_new_issue_files(
    directory: str,
) -> tuple[NewIssuesDefault, list[RecipientEntry]]:
    """Loads `default.yaml` and every other recipient file in `directory`.

    Tree keys match a subscription url. Hardware keys match a platform and,
    when the entry omits origin, use that platform's origin.
    """
    path = os.path.join(directory, DEFAULT_FILE)
    try:
        default = NewIssuesDefault.model_validate(_read_yaml(path))
    except ValidationError as exc:
        error = exc.errors()[0]
        key = error["loc"][0] if error["loc"] else None
        raise RecipientFileError(path, error["msg"], key=key) from exc
    for issue in default.issues:
        if issue not in NEW_ISSUE_KINDS:
            raise RecipientFileError(path, f"issue '{issue}' not allowed", key="issues")
    entries = _collect_entries(
        directory,
        allowed_keys=NEW_ISSUE_KEYS,
        allowed_issues=NEW_ISSUE_KINDS,
        allow_hardware=True,
        subscriptions_directory=_subscriptions_directory(directory),
    )
    return default, entries
