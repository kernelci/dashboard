from collections import defaultdict
import json
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.logger import log_message
from django.utils.decorators import method_decorator
from datetime import datetime, timezone
from django.views.decorators.csrf import csrf_exempt
from kernelCI_app.helpers.trees import make_tree_identifier_key
from kernelCI_app.queries.hardware import get_hardware_commit_history
from kernelCI_app.typeModels.commonOpenApiParameters import (
    HARDWARE_ID_PATH_PARAM,
)
from kernelCI_app.typeModels.hardwareDetails import (
    CommitHistoryPostBody,
    CommitHistoryValidCheckout,
    HardwareCommitHistoryResponse,
)
from pydantic import ValidationError
from http import HTTPStatus
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


# disable django csrf protection https://docs.djangoproject.com/en/5.0/ref/csrf/
# that protection is recommended for ‘unsafe’ methods (POST, PUT, and DELETE)
# but we are using POST here just to follow the convention to use the request body
# also the csrf protection require the usage of cookies which is not currently
# supported in this project
@method_decorator(csrf_exempt, name="dispatch")
class HardwareDetailsCommitHistoryView(APIView):
    def _sanitize_checkouts(self, rows):
        formatted_checkouts = defaultdict(list)

        for checkout in rows:
            dict_checkout = {
                "tree_name": checkout[0],
                "git_repository_url": checkout[1],
                "git_repository_branch": checkout[2],
                "git_commit_tags": checkout[3],
                "git_commit_name": checkout[4],
                "git_commit_hash": checkout[5],
                "start_time": checkout[6],
            }
            try:
                validate_checkout = CommitHistoryValidCheckout(**dict_checkout)
                table_response_key = make_tree_identifier_key(
                    tree_name=validate_checkout.tree_name,
                    git_repository_url=validate_checkout.git_repository_url,
                    git_repository_branch=validate_checkout.git_repository_branch,
                )

                formatted_checkouts[table_response_key].append(
                    validate_checkout.model_dump()
                )
            except ValidationError as e:
                log_message(f"Error validating checkout {dict_checkout}: {e.json()}")
                continue

        return formatted_checkouts

    # Using post to receive a body request
    @extend_schema(
        parameters=[HARDWARE_ID_PATH_PARAM],
        responses=HardwareCommitHistoryResponse,
        request=CommitHistoryPostBody,
        methods=["POST"],
    )
    def post(self, request, hardware_id) -> Response:
        try:
            body = json.loads(request.body)

            post_body = CommitHistoryPostBody(**body)

            origin = post_body.origin
            end_datetime = datetime.fromtimestamp(
                int(post_body.endTimestampInSeconds), timezone.utc
            )
            start_datetime = datetime.fromtimestamp(
                int(post_body.startTimestampInSeconds), timezone.utc
            )
            commit_heads = post_body.commitHeads
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError:
            return create_api_error_response(
                error_message="Invalid body, request body must be a valid json string"
            )
        except (ValueError, TypeError):
            return create_api_error_response(
                error_message="startTimestampInSeconds and endTimestampInSeconds must be a Unix Timestamp"
            )

        commit_history_data = get_hardware_commit_history(
            origin=origin,
            start_date=start_datetime,
            end_date=end_datetime,
            commit_heads=commit_heads,
        )

        if not commit_history_data:
            return create_api_error_response(
                error_message="Commit history not found", status_code=HTTPStatus.OK
            )

        commit_history = self._sanitize_checkouts(commit_history_data)

        try:
            valid_response = HardwareCommitHistoryResponse(
                commit_history_table=commit_history
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
