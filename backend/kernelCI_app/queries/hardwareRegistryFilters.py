from dataclasses import astuple, dataclass
from typing import Optional

from django.db import connection

_CATALOG_COLUMNS = (
    ("architecture", "proc.architecture"),
    ("processor", "proc.id"),
    ("platform_vendor", "plat.vendor_id"),
    ("silicon_vendor", "proc.vendor_id"),
    ("system_module", "plat.system_module_id"),
    ("form_factor", "plat.form_factor"),
    ("board_type", "plat.type"),
)


def normalize_csv(value: object) -> tuple[str, ...]:
    if not isinstance(value, str):
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


@dataclass(frozen=True)
class HardwareRegistryFilter:
    architecture: tuple[str, ...] = ()
    processor: tuple[str, ...] = ()
    platform_vendor: tuple[str, ...] = ()
    silicon_vendor: tuple[str, ...] = ()
    platform: tuple[str, ...] = ()
    system_module: tuple[str, ...] = ()
    form_factor: tuple[str, ...] = ()
    board_type: tuple[str, ...] = ()

    def is_empty(self) -> bool:
        return not any(astuple(self))


def hardware_registry_filter_from_request(params) -> HardwareRegistryFilter:
    return HardwareRegistryFilter(
        architecture=normalize_csv(params.get("architecture")),
        processor=normalize_csv(params.get("processor")),
        platform_vendor=normalize_csv(params.get("platformVendor")),
        silicon_vendor=normalize_csv(params.get("siliconVendor")),
        platform=normalize_csv(params.get("platform")),
        system_module=normalize_csv(params.get("systemModule")),
        form_factor=normalize_csv(params.get("formFactor")),
        board_type=normalize_csv(params.get("boardType")),
    )


def registry_filter_predicate(
    registry_filter: HardwareRegistryFilter, platform_sql: str
) -> tuple[Optional[str], dict]:
    """Same field is OR (`= ANY`). Different fields are AND.

    A platform missing from the registry matches only when the platform id
    is the sole selected field.
    """
    if registry_filter.is_empty():
        return None, {}

    platform_only = bool(registry_filter.platform) and all(
        not getattr(registry_filter, name) for name, _column in _CATALOG_COLUMNS
    )
    if platform_only:
        return (
            f"{platform_sql} = ANY(%(platform)s)",
            {"platform": list(registry_filter.platform)},
        )

    params: dict = {}
    catalog: list[str] = []
    for name, column in _CATALOG_COLUMNS:
        values = getattr(registry_filter, name)
        if values:
            params[name] = list(values)
            catalog.append(f"{column} = ANY(%({name})s)")
    if registry_filter.platform:
        params["platform"] = list(registry_filter.platform)
        catalog.append("plat.id = ANY(%(platform)s)")

    registered = f"""
        {platform_sql} IN (
            SELECT plat.id
            FROM hardware_registry_platforms plat
            INNER JOIN hardware_registry_processors proc
                ON proc.id = plat.processor_id
            WHERE {" AND ".join(catalog)}
        )
    """
    return registered, params


def get_hardware_registry_filter_options(platforms: list[str]) -> dict[str, list[str]]:
    """Distinct registry values for the platforms in the current listing.

    Platform ids include boards that are not in the registry. The other lists
    do not: those boards have no architecture, vendor, or board type to offer.
    """
    query = """
        WITH registered AS (
            SELECT
                plat.vendor_id AS platform_vendor,
                plat.type AS board_type,
                plat.form_factor,
                plat.system_module_id AS system_module,
                proc.id AS processor,
                proc.architecture,
                proc.vendor_id AS silicon_vendor
            FROM hardware_registry_platforms plat
            INNER JOIN hardware_registry_processors proc
                ON proc.id = plat.processor_id
            WHERE plat.id = ANY(%(platforms)s)
        )
        SELECT
            ARRAY(
                SELECT DISTINCT architecture FROM registered
                WHERE architecture IS NOT NULL AND architecture <> ''
                ORDER BY 1
            ),
            ARRAY(SELECT DISTINCT processor FROM registered ORDER BY 1),
            ARRAY(SELECT DISTINCT platform_vendor FROM registered ORDER BY 1),
            ARRAY(SELECT DISTINCT silicon_vendor FROM registered ORDER BY 1),
            ARRAY(
                SELECT DISTINCT system_module FROM registered
                WHERE system_module IS NOT NULL AND system_module <> ''
                ORDER BY 1
            ),
            ARRAY(
                SELECT DISTINCT form_factor FROM registered
                WHERE form_factor IS NOT NULL AND form_factor <> ''
                ORDER BY 1
            ),
            ARRAY(
                SELECT DISTINCT board_type FROM registered
                WHERE board_type IS NOT NULL AND board_type <> ''
                ORDER BY 1
            )
    """
    names = (
        "architecture",
        "processor",
        "platform_vendor",
        "silicon_vendor",
        "system_module",
        "form_factor",
        "board_type",
    )
    with connection.cursor() as cursor:
        cursor.execute(query, {"platforms": platforms})
        row = cursor.fetchone()
    options = {name: list(row[index] or []) for index, name in enumerate(names)}
    options["platform"] = sorted(set(platforms))
    return options
