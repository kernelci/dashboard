import json
from typing import Any

import jsonschema


class Schema:
    """PostgreSQL database schema v5.3"""

    # The schema's version.
    version = (5, 3)

    # The relationship graph between the tables/models.
    graph = {
        "": ["checkouts", "issues"],
        "checkouts": ["builds"],
        "builds": ["tests", "incidents"],
        "tests": ["incidents"],
        "issues": ["incidents"],
        "incidents": [],
    }

    def __init__(self):
        with open("kernelCI_ingester/data/schema/v05.03.json", "r") as f:
            self.schema = json.load(f)

    def upgrade_previous(self, object_at_previous_version: dict[str, Any]):
        """
        Upgrade the previous schema version to this one. This includes:

        Adding new optional fields,
        adding new required fields with default value,
        removing old fields,
        renaming old field,
        changing a field's definition (same name, different type).

        This method has to be written manually.
        """
        pass

    def validate(self, object: dict[str, Any]):
        """
        Validate the object against the schema.
        """

        jsonschema.validate(instance=object, schema=self.schema)
