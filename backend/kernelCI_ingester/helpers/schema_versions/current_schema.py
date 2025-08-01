from kernelCI_ingester.helpers.schema_versions.v05_03 import Schema as Schema_5_3

CURRENT_SCHEMA = (5, 3)

# TODO: Use this schema map to validate older schema versions
SCHEMA_MAP = {
    (5, 3): Schema_5_3,
}


class CurrentSchema(SCHEMA_MAP[CURRENT_SCHEMA]):
    """
    This class should be the "interface" used in the code.

    To update the current used schema, simply change the parent class
    """

    pass
