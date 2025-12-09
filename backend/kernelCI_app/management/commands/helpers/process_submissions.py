import logging
from django.utils import timezone
from typing import Any, TypedDict

from django.db import IntegrityError

from kernelCI_app.constants.ingester import INGESTER_GRAFANA_LABEL
from pydantic import ValidationError

from kernelCI_app.models import Builds, Checkouts, Incidents, Issues, Tests
from kernelCI_app.typeModels.modelTypes import TableNames
from prometheus_client import Counter


class ProcessedSubmission(TypedDict):
    """Stores the list of items in a single submission.
    Lists can't be None but can be empty."""

    issues: list[Issues]
    checkouts: list[Checkouts]
    builds: list[Builds]
    tests: list[Tests]
    incidents: list[Incidents]


logger = logging.getLogger(__name__)


def get_model_fields(model_fields) -> set[str]:
    """
    Gathers a set of the field_names of a model in order to validate them.
    This is done such that django doesn't complain about extra fields in a model.
    """
    valid_fields = set()
    for field in model_fields:
        if field.__class__.__name__ == "ForeignKey":
            valid_fields.add(f"{field.name}_id")
        else:
            valid_fields.add(field.name)
    return valid_fields


ISSUE_FIELDS = get_model_fields(Issues._meta.get_fields())
CHECKOUT_FIELDS = get_model_fields(Checkouts._meta.get_fields())
BUILD_FIELDS = get_model_fields(Builds._meta.get_fields())
TEST_FIELDS = get_model_fields(Tests._meta.get_fields())
INCIDENT_FIELDS = get_model_fields(Incidents._meta.get_fields())


def flatten_dict_specific(target: dict[str, Any], target_fields: list[str]):
    """
    Flatten specific fields of a dict on a one-level-deep only.
    Done in order to avoid flattening fields that should be kept as JSONs
     (which happens with other libraries such as flatdict).

    Example of `flatten_dict_specific(test_data, ["environment"])`:
    `test_data` will go from
    ```
    {
        environment: {
            comment: "foo"
            misc: {
                platform: "bar"
            }
        }
    }
    ```
    to
    ```
    {
        environment_comment: "foo"
        environment_misc: {
            platform: "bar"
        }
    }
    """

    separator = "_"

    flattened_dict = target.copy()
    for first_key, value in target.items():
        if first_key in target_fields:
            if isinstance(value, dict):
                for (
                    inner_key,
                    real_value,
                ) in value.items():
                    merged_key = separator.join([first_key, inner_key])
                    flattened_dict[merged_key] = real_value
                del flattened_dict[first_key]
            else:
                print(f"Target key {first_key} is not a dict")
                continue

    return flattened_dict


def make_issue_instance(issue: dict[str, Any]) -> Issues:
    flattened_issue = flatten_dict_specific(issue, ["culprit"])
    filtered_issue = {
        key: value for key, value in flattened_issue.items() if key in ISSUE_FIELDS
    }
    obj = Issues(**filtered_issue)
    obj.field_timestamp = timezone.now()
    return obj


def make_checkout_instance(checkout: dict[str, Any]) -> Checkouts:
    filtered_checkout = {
        key: value for key, value in checkout.items() if key in CHECKOUT_FIELDS
    }
    obj = Checkouts(**filtered_checkout)
    obj.field_timestamp = timezone.now()
    return obj


def make_build_instance(build: dict[str, Any]) -> Builds:
    filtered_build = {key: value for key, value in build.items() if key in BUILD_FIELDS}
    obj = Builds(**filtered_build)
    obj.field_timestamp = timezone.now()
    return obj


def make_test_instance(test: dict[str, Any]) -> Tests:
    flattened_test = flatten_dict_specific(test, ["environment", "number"])
    filtered_test = {
        key: value for key, value in flattened_test.items() if key in TEST_FIELDS
    }
    obj = Tests(**filtered_test)
    obj.field_timestamp = timezone.now()
    return obj


def make_incident_instance(incident: dict[str, Any]) -> Incidents:
    filtered_incident = {
        key: value for key, value in incident.items() if key in INCIDENT_FIELDS
    }
    obj = Incidents(**filtered_incident)
    obj.field_timestamp = timezone.now()
    return obj


def build_instances_from_submission(
    data: dict[str, Any], counters: dict[TableNames, Counter]
) -> ProcessedSubmission:
    """
    Convert raw submission dicts into unsaved Django model instances, grouped by type.
    Per-item errors are logged and the item is skipped, matching the previous behavior.

    Params:
        data: the submission data in dict format
        counters: a dict mapping tables to its prometheus counter
    """
    out: ProcessedSubmission = {
        "issues": [],
        "checkouts": [],
        "builds": [],
        "tests": [],
        "incidents": [],
    }

    def _process(items, item_type: TableNames):
        if not items:
            return
        for item in items:
            if not isinstance(item, dict):
                logger.warning(
                    f"{item_type.capitalize()} data is not a dict, its type is: {type(item)}"
                )
                continue
            try:
                match item_type:
                    case "issues":
                        issue = make_issue_instance(item)
                        out["issues"].append(issue)
                        counters["issues"].labels(
                            ingester=INGESTER_GRAFANA_LABEL, origin=issue.origin
                        ).inc()
                    case "checkouts":
                        checkout = make_checkout_instance(item)
                        out["checkouts"].append(checkout)
                        counters["checkouts"].labels(
                            ingester=INGESTER_GRAFANA_LABEL, origin=checkout.origin
                        ).inc()
                    case "builds":
                        build = make_build_instance(item)
                        out["builds"].append(build)

                        try:
                            misc = build.misc
                            lab = misc.get("lab")
                        except AttributeError:
                            lab = None

                        counters["builds"].labels(
                            ingester=INGESTER_GRAFANA_LABEL,
                            origin=build.origin,
                            lab=lab,
                        ).inc()
                    case "tests":
                        test = make_test_instance(item)
                        out["tests"].append(test)

                        try:
                            misc = test.misc
                            lab = misc.get("lab", misc.get("runtime"))
                        except AttributeError:
                            lab = None

                        try:
                            environment_misc = test.environment_misc
                            platform = environment_misc.get("platform")
                        except AttributeError:
                            platform = None

                        counters["tests"].labels(
                            ingester=INGESTER_GRAFANA_LABEL,
                            origin=test.origin,
                            lab=lab,
                            platform=platform,
                        ).inc()
                    case "incidents":
                        incident = make_incident_instance(item)
                        out["incidents"].append(incident)
                        counters["incidents"].labels(
                            ingester=INGESTER_GRAFANA_LABEL, origin=incident.origin
                        ).inc()
                    case _:
                        raise ValueError(f"Unknown item type: {item_type}")
            except ValidationError as ve:
                logger.error(f"Validation error for {item_type} item: {ve}")
                continue
            except Exception as e:
                logger.error(f"{e.__class__.__name__} error for {item_type} item: {e}")
                continue

    _process(data.get("issues"), "issues")
    _process(data.get("checkouts"), "checkouts")
    _process(data.get("builds"), "builds")
    _process(data.get("tests"), "tests")
    _process(data.get("incidents"), "incidents")

    return out


def insert_items(
    item_type: TableNames,
    items: list[dict[str, Any]],
):
    logger.info(f"Processing {len(items)} {item_type}")
    item_counter = 0
    success_counter = 0

    for item in items:
        if not isinstance(item, dict):
            logger.warning(
                f"{item_type.capitalize()} data is not a dict, its type is: {type(item)}"
            )
            continue
        item_counter += 1

        try:
            match item_type:
                case "issues":
                    model_instance = make_issue_instance(item)
                case "checkouts":
                    model_instance = make_checkout_instance(item)
                case "builds":
                    model_instance = make_build_instance(item)
                case "tests":
                    model_instance = make_test_instance(item)
                case "incidents":
                    model_instance = make_incident_instance(item)
                case _:
                    raise ValueError(f"Unknown item type: {item_type}")

            model_instance.save()
            success_counter += 1
        except ValidationError as ve:
            logger.error(f"Validation error for {item_type} item: {ve}")
            continue
        # TODO: catch whenever there is a problem with the schema and deal with it
        except IntegrityError as ie:
            logger.error(f"Integrity error for {item_type} item: {ie}")
            continue
        except Exception as e:
            logger.error(f"{e.__class__.__name__} error for {item_type} item: {e}")
            continue

    print(f"Processed {item_counter} {item_type}, {success_counter} succeeded")
    return success_counter


def insert_submission_data(data: dict[str, Any], metadata: dict[str, Any]):
    """
    Processes the data from a submission file.
    """
    logger.info(
        "Processing submission data for %s", metadata.get("filename", "unknown")
    )

    try:
        # Note that the order of processing is important, as some data depends on others
        # Checkouts > Builds > Tests
        # Issues && Builds && Tests > Incidents
        if issues := data.get("issues"):
            insert_items("issues", issues)
        if checkouts := data.get("checkouts"):
            insert_items("checkouts", checkouts)
        if builds := data.get("builds"):
            insert_items("builds", builds)
        if tests := data.get("tests"):
            insert_items("tests", tests)
        if incidents := data.get("incidents"):
            insert_items("incidents", incidents)
    except Exception as e:
        logger.error(f"Error processing submission data: {e}")
        raise e

    logger.info(
        "Successfully parsed %s submission file", metadata.get("filename", "unknown")
    )
