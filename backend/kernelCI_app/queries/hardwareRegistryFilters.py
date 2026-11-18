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


def registry_id(platform: str) -> str:
    """Daily rows store `vendor,board`. The registry stores `board`."""
    return platform.partition(",")[2] or platform


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
    """Repeated query parameters, not comma-separated: a platform id holds a comma."""

    def values(name: str) -> tuple[str, ...]:
        return tuple(
            value.strip() for value in params.getlist(name) if value and value.strip()
        )

    return HardwareRegistryFilter(
        architecture=values("architecture"),
        processor=values("processor"),
        platform_vendor=values("platformVendor"),
        silicon_vendor=values("siliconVendor"),
        platform=values("platform"),
        system_module=values("systemModule"),
        form_factor=values("formFactor"),
        board_type=values("boardType"),
    )


def registry_filter_predicate(
    registry_filter: HardwareRegistryFilter, platform_sql: str
) -> tuple[Optional[str], dict]:
    """Same field is OR (`= ANY`). Different fields are AND.

    Platform ids match the daily rows as they are. The other fields go through
    the registry, so a platform missing from it drops out as soon as one of
    them is set.
    """
    if registry_filter.is_empty():
        return None, {}

    params: dict = {}
    catalog: list[str] = []
    for name, column in _CATALOG_COLUMNS:
        values = getattr(registry_filter, name)
        if values:
            params[name] = list(values)
            catalog.append(f"{column} = ANY(%({name})s)")

    conditions: list[str] = []
    if catalog:
        conditions.append(f"""
        COALESCE(NULLIF(split_part({platform_sql}, ',', 2), ''), {platform_sql}) IN (
            SELECT plat.id
            FROM hardware_registry_platforms plat
            INNER JOIN hardware_registry_processors proc
                ON proc.id = plat.processor_id
            WHERE {" AND ".join(catalog)}
        )
    """)
    if registry_filter.platform:
        params["platform"] = list(registry_filter.platform)
        conditions.append(f"{platform_sql} = ANY(%(platform)s)")

    return " AND ".join(conditions), params


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
            WHERE plat.id = ANY(%(registry_ids)s)
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
        cursor.execute(
            query, {"registry_ids": sorted({registry_id(p) for p in platforms})}
        )
        row = cursor.fetchone()
    options = {name: list(row[index] or []) for index, name in enumerate(names)}
    options["platform"] = sorted(set(platforms))
    return options
