import logging
from django.utils import timezone
from typing import Any, Literal

from django.db import IntegrityError
from pydantic import ValidationError

from kernelCI_app.models import Builds, Checkouts, Incidents, Issues, Tests


logger = logging.getLogger(__name__)


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


def save_issue(issue) -> None:
    flattened_issue_data = flatten_dict_specific(issue, ["culprit"])
    valid_issue = Issues(**flattened_issue_data)
    valid_issue.field_timestamp = timezone.now()
    valid_issue.save()
    return


def save_checkout(checkout) -> None:
    valid_checkout = Checkouts(**checkout)
    valid_checkout.field_timestamp = timezone.now()
    valid_checkout.save()
    return


def save_build(build) -> None:
    valid_build = Builds(**build)
    valid_build.field_timestamp = timezone.now()
    valid_build.save()
    return


def save_test(test: dict[str, Any]) -> None:
    flattened_test_data = flatten_dict_specific(test, ["environment", "number"])
    valid_test = Tests(**flattened_test_data)
    valid_test.field_timestamp = timezone.now()
    valid_test.save()
    return


def save_incident(incident) -> None:
    valid_incident = Incidents(**incident)
    valid_incident.field_timestamp = timezone.now()
    valid_incident.save()
    return


def process_items(
    item_type: Literal["issues", "checkouts", "builds", "tests", "incidents"],
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
            # TODO: pass the timestamp at insertion
            match item_type:
                case "issues":
                    save_issue(item)
                case "checkouts":
                    save_checkout(item)
                case "builds":
                    save_build(item)
                case "tests":
                    save_test(item)
                case "incidents":
                    save_incident(item)
                case _:
                    raise ValueError(f"Unknown item type: {item_type}")
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


def process_submission_data(data: dict[str, Any], metadata: dict[str, Any]):
    """
    Processes the data from a submission file.
    """
    logger.info(f"Processing submission data for {metadata.get('filename', 'unknown')}")

    try:
        # Note that the order of processing is important, as some data depends on others
        # Checkouts > Builds > Tests
        # Issues && Builds && Tests > Incidents
        if issues := data.get("issues"):
            process_items("issues", issues)
        if checkouts := data.get("checkouts"):
            process_items("checkouts", checkouts)
        if builds := data.get("builds"):
            process_items("builds", builds)
        if tests := data.get("tests"):
            process_items("tests", tests)
        if incidents := data.get("incidents"):
            process_items("incidents", incidents)
    except Exception as e:
        logger.error(f"Error processing submission data: {e}")
        raise e

    logger.info(
        f"Successfully parsed {metadata.get('filename', 'unknown')} submission file"
    )
