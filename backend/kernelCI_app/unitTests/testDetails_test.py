from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.testClient import TestClient
from kernelCI_app.unitTests.utils.defaultTestAsserts import defaultTestAsserts
import pytest


@online
@pytest.mark.parametrize(
    "test_id, status_code, has_error_body",
    [
        ("maestro:67b898cdf7707533c0067a02", 200, False),
        ("invalid_id", 200, True),
    ],
)
def test_get(test_id, status_code, has_error_body):
    client = TestClient()
    response = client.get_test_details(test_id=test_id)
    defaultTestAsserts(response, status_code, has_error_body)
