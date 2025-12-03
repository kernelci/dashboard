from django.core.management.base import BaseCommand
from kernelCI_app.typeModels.modelTypes import MODEL_MAP
import os
from datetime import datetime
from jinja2 import Template


class Command(BaseCommand):
    help = """
    Dynamically generates the insert queries for all models, storing them in a specific file.
    Gives priority to the existing data in the database.

    This command should not executed in runtime.
    """

    def add_arguments(self, parser):
        # Add custom command arguments here
        pass

    def handle(self, *args, **options):
        var_insert_queries = {}

        for table_name in MODEL_MAP.keys():
            model = MODEL_MAP[table_name]

            updateable_model_fields: list[str] = []
            updateable_db_fields: list[str] = []
            query_params_properties: list[tuple[str, str]] = []

            for field in model._meta.fields:
                if field.generated:
                    continue

                field_name = (
                    field.name + "_id"
                    if field.get_internal_type() == "ForeignKey"
                    else field.name
                )
                real_name = field.db_column or field_name
                updateable_model_fields.append(field_name)
                updateable_db_fields.append(real_name)

                operation = "GREATEST" if real_name == "_timestamp" else "COALESCE"
                # Fields that are never null don't need to have conflict clauses (except _timestamp)
                if field.null or real_name == "_timestamp":
                    query_params_properties.append((real_name, operation))

            updateable_db_fields_clauses = [
                f"""
                    {updateable_field}"""
                for updateable_field in updateable_db_fields
            ]

            conflict_clauses = []
            for field, op in query_params_properties:
                conflict_clauses.append(
                    f"""
                    {field} = {op}({table_name}.{field}, EXCLUDED.{field})"""
                )

            query = f"""
                INSERT INTO {table_name} ({','.join(updateable_db_fields_clauses)}
                )
                VALUES (
                    {', '.join(['%s'] * len(updateable_db_fields))}
                )
                ON CONFLICT (id)
                DO UPDATE SET{','.join(conflict_clauses)};
            """

            var_insert_queries[table_name] = {}
            var_insert_queries[table_name][
                "updateable_model_fields"
            ] = updateable_model_fields
            var_insert_queries[table_name]["query"] = query

        # Read the template file
        template_path = os.path.join(
            os.path.dirname(__file__), "templates", "insert_queries.txt.j2"
        )
        with open(template_path, "r") as template_file:
            template_content = template_file.read()

        # Render the template with the variables
        template = Template(template_content)
        rendered_content = template.render(
            timestamp=datetime.now(),
            checkouts=var_insert_queries["checkouts"],
            issues=var_insert_queries["issues"],
            builds=var_insert_queries["builds"],
            tests=var_insert_queries["tests"],
            incidents=var_insert_queries["incidents"],
        )

        # Write the result to a Python file
        output_path = os.path.join(
            os.path.dirname(__file__), "generated", "insert_queries.py"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as output_file:
            output_file.write(rendered_content)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated insert queries at {output_path}"
            )
        )
