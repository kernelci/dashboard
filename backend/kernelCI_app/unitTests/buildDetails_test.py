from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.buildClient import BuildClient
from kernelCI_app.unitTests.utils.defaultTestAsserts import defaultTestAsserts
import pytest


@online
@pytest.mark.parametrize(
    "build_id, status_code, has_error_body",
    [
        ("maestro:67b62592f7707533c0ff7a95", 200, False),
        ("invalid_id", 200, True),
    ],
)
def test_get(build_id, status_code, has_error_body):
    client = BuildClient()
    response = client.get_build_details(build_id=build_id)
    defaultTestAsserts(response, status_code, has_error_body)
