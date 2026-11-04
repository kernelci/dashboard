from email.utils import getaddresses
from pathlib import Path

import yaml
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from kernelCI_app.typeModels.metrics_notifications import MetricsReportData


class MetricsRuleError(Exception):
    def __init__(self, *, file: str, rule: str, key: str, message: str):
        self.file = file
        self.rule = rule
        self.key = key
        self.message = message
        super().__init__(self._format())

    def _format(self) -> str:
        head = self.file
        if self.rule:
            head = f"{head}: rule {self.rule}"
        if self.key:
            head = f"{head}: key {self.key}"
        return f"{head}: {self.message}"


class DuplicateYamlKeyError(Exception):
    def __init__(self, key: object):
        self.key = key
        super().__init__(str(key))


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(loader: _UniqueKeyLoader, node, deep=False):
    loader.flatten_mapping(node)
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise DuplicateYamlKeyError(key)
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


class MetricsRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    to: list[str] = Field(min_length=1)
    period_days: int = Field(gt=0)
    origins: list[str] | None = None
    labs: list[str] | None = None

    @field_validator("to")
    @classmethod
    def to_are_single_addresses(cls, value: list[str]) -> list[str]:
        for item in value:
            parsed = getaddresses([item])
            try:
                if len(parsed) != 1:
                    raise DjangoValidationError("more than one address")
                validate_email(parsed[0][1])
            except DjangoValidationError as exc:
                raise ValueError("must be a single email address") from exc
        return value

    @field_validator("origins", "labs")
    @classmethod
    def entries_are_non_empty(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        if any(not item.strip() for item in value):
            raise ValueError("entries must be non-empty")
        return value


def metrics_rules_dir() -> Path:
    return Path(settings.BACKEND_DATA_DIR) / "notifications" / "metrics"


def load_metrics_rules(directory: Path | None = None) -> list[MetricsRule]:
    directory = directory or metrics_rules_dir()
    if not directory.is_dir():
        return []

    seen: dict[str, Path] = {}
    loaded: list[MetricsRule] = []
    for path in sorted(directory.glob("*.yaml")):
        loaded.extend(_load_metrics_file(path, seen))
    return loaded


def _load_yaml(text: str):
    loader = _UniqueKeyLoader(text)
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()


def _load_metrics_file(path: Path, seen: dict[str, Path]) -> list[MetricsRule]:
    try:
        data = _load_yaml(path.read_text())
    except DuplicateYamlKeyError as exc:
        raise MetricsRuleError(
            file=path.name,
            rule=str(exc.key),
            key=str(exc.key),
            message="duplicate key",
        ) from exc
    except yaml.YAMLError as exc:
        raise MetricsRuleError(
            file=path.name,
            rule="",
            key="",
            message=str(exc),
        ) from exc

    if data is None:
        return []
    if not isinstance(data, dict):
        raise MetricsRuleError(
            file=path.name,
            rule="",
            key="",
            message="file must be a mapping of rule names",
        )

    loaded: list[MetricsRule] = []
    for name, body in data.items():
        if not isinstance(name, str) or not name:
            raise MetricsRuleError(
                file=path.name,
                rule=str(name),
                key=str(name),
                message="rule name must be a non-empty string",
            )
        if name in seen:
            raise MetricsRuleError(
                file=path.name,
                rule=name,
                key=name,
                message=f"duplicate rule name, already defined in {seen[name].name}",
            )
        if not isinstance(body, dict):
            raise MetricsRuleError(
                file=path.name,
                rule=name,
                key="",
                message="rule must be a mapping",
            )
        try:
            rule = MetricsRule.model_validate(body)
        except ValidationError as exc:
            err = exc.errors()[0]
            key = str(err["loc"][0]) if err["loc"] else ""
            raise MetricsRuleError(
                file=path.name,
                rule=name,
                key=key,
                message=err["msg"],
            ) from exc
        seen[name] = path
        loaded.append(rule)
    return loaded


def _keep(mapping: dict, names: list[str]) -> dict:
    chosen = set(names)
    return {key: value for key, value in mapping.items() if key in chosen}


def scope_metrics_data(data: MetricsReportData, rule: MetricsRule) -> MetricsReportData:
    updates = {}
    if rule.origins is not None:
        updates["build_incidents_by_origin"] = _keep(
            data.build_incidents_by_origin, rule.origins
        )
        updates["top_issues_by_origin"] = _keep(data.top_issues_by_origin, rule.origins)
        updates["new_issues_by_origin"] = _keep(data.new_issues_by_origin, rule.origins)
    if rule.labs is not None:
        updates["lab_maps"] = _keep(data.lab_maps, rule.labs)
        updates["prev_lab_maps"] = _keep(data.prev_lab_maps, rule.labs)
    if not updates:
        return data
    return data.model_copy(update=updates)
