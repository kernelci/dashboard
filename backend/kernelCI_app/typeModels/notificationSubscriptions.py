"""Subscription YAML and metrics rules. Sending behavior is unchanged."""

from email.utils import parseaddr
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    model_validator,
)

IssueKind = Literal["build", "boot", "test"]


class NotificationConfigError(Exception):
    def __init__(self, file: str, field: str, message: str):
        self.file = file
        self.field = field
        super().__init__(f"{file}: {field}: {message}")


def validate_address(value: str) -> str:
    _, address = parseaddr(value)
    local, separator, domain = address.partition("@")
    if not separator or not local or not domain or "@" in domain:
        raise ValueError(f"invalid email address: {value}")
    return value


Address = Annotated[str, AfterValidator(validate_address)]


class Recipient(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Address
    issues: list[IssueKind] | None = Field(default=None, min_length=1)

    @model_validator(mode="before")
    @classmethod
    def from_address(cls, value):
        if isinstance(value, str):
            return {"email": value}
        return value


_RECIPIENTS = TypeAdapter(list[Recipient])


def cc_addresses(recipients: list) -> list[str]:
    """Addresses passed to current mails."""
    return [item.email for item in _RECIPIENTS.validate_python(recipients)]


class TreeSubscription(BaseModel):
    model_config = ConfigDict(extra="allow")

    url: str
    default_recipients: list[Recipient] = []


class HardwareSubscription(BaseModel):
    model_config = ConfigDict(extra="allow")

    default_recipients: list[Recipient] = []
    origin: str | None = None


class MetricsRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recipients: list[Address] = Field(min_length=1)
    hardware: list[str] = []
    trees: list[str] = []
    origins: list[str] = []
    period_days: int = Field(gt=0)


def is_hardware_filename(name: str) -> bool:
    return name.endswith("_hardware.yaml") or name.endswith("_hardware.yml")


def _yaml_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix in {".yaml", ".yml"}
    )


def _load_mapping(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise NotificationConfigError(
            path.name, "<file>", f"invalid YAML: {exc}"
        ) from exc
    if not isinstance(data, dict) or not data:
        raise NotificationConfigError(path.name, "<file>", "expected a mapping")
    return data


def _validation_error(
    path: Path, exc: ValidationError, *, prefix: str = ""
) -> NotificationConfigError:
    err = exc.errors()[-1]
    field = ".".join(str(part) for part in err["loc"]) or "<file>"
    if prefix:
        field = f"{prefix}.{field}"
    return NotificationConfigError(path.name, field, err["msg"])


def load_subscriptions(directory: Path) -> tuple[set[str], set[str]]:
    """Validate every subscription file. Returns tree names and hardware names."""
    trees: set[str] = set()
    hardware: set[str] = set()
    for path in _yaml_files(directory):
        data = _load_mapping(path)
        hardware_file = is_hardware_filename(path.name)
        model = TypeAdapter(
            dict[str, HardwareSubscription]
            if hardware_file
            else dict[str, TreeSubscription]
        )
        try:
            parsed = model.validate_python(data)
        except ValidationError as exc:
            raise _validation_error(path, exc) from exc
        names = hardware if hardware_file else trees
        names.update(parsed)
    return trees, hardware


def load_metrics_rules(directory: Path, *, trees: set[str], hardware: set[str]) -> None:
    """Validate metrics rules against subscription names. Does not send mail."""
    seen: dict[str, tuple[str, MetricsRule]] = {}
    for path in _yaml_files(directory):
        data = _load_mapping(path)
        for name, body in data.items():
            if name in seen:
                other = seen[name][0]
                raise NotificationConfigError(
                    path.name,
                    name,
                    f"duplicate rule name, also in {other}",
                )
            try:
                rule = MetricsRule.model_validate(body)
            except ValidationError as exc:
                raise _validation_error(path, exc, prefix=name) from exc
            _check_rule_names(path, name, rule, trees=trees, hardware=hardware)
            _check_overlap(path, name, rule, seen)
            seen[name] = (path.name, rule)


def _check_rule_names(
    path: Path,
    name: str,
    rule: MetricsRule,
    *,
    trees: set[str],
    hardware: set[str],
) -> None:
    for platform in rule.hardware:
        if platform not in hardware:
            raise NotificationConfigError(
                path.name,
                f"{name}.hardware",
                f"unknown hardware {platform}",
            )
    for tree in rule.trees:
        if tree not in trees:
            raise NotificationConfigError(
                path.name,
                f"{name}.trees",
                f"unknown tree {tree}",
            )


def _check_overlap(
    path: Path,
    name: str,
    rule: MetricsRule,
    seen: dict[str, tuple[str, MetricsRule]],
) -> None:
    for other_name, (other_file, other) in seen.items():
        shared_recipients = set(rule.recipients) & set(other.recipients)
        shared_hardware = set(rule.hardware) & set(other.hardware)
        shared_trees = set(rule.trees) & set(other.trees)
        if not shared_recipients or not (shared_hardware or shared_trees):
            continue
        scope = ", ".join(sorted(shared_hardware | shared_trees))
        people = ", ".join(sorted(shared_recipients))
        raise NotificationConfigError(
            path.name,
            f"{name}.recipients",
            f"overlaps {other_name} in {other_file} for {people} on {scope}",
        )
