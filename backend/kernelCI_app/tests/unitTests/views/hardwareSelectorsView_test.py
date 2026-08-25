from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.views.hardwareSelectorsView import HardwareSelectorsView


class TestHardwareSelectorsView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch(
        "kernelCI_app.views.hardwareSelectorsView.get_hardware_selectors",
        return_value=[],
    )
    def test_build_origin_is_optional(self, mock_get_selectors):
        HardwareSelectorsView().get(
            self.factory.get("/hardware/selectors", {"buildOrigin": ""})
        )

        mock_get_selectors.assert_called_once_with(build_origin=None)

    @patch(
        "kernelCI_app.views.hardwareSelectorsView.get_hardware_selectors",
        return_value=[],
    )
    def test_defaults_to_maestro(self, mock_get_selectors):
        HardwareSelectorsView().get(self.factory.get("/hardware/selectors"))

        mock_get_selectors.assert_called_once_with(build_origin=[DEFAULT_ORIGIN])

    @patch(
        "kernelCI_app.views.hardwareSelectorsView.get_hardware_selectors",
        return_value=[],
    )
    def test_honours_deprecated_origin(self, mock_get_selectors):
        HardwareSelectorsView().get(
            self.factory.get("/hardware/selectors", {"origin": "legacy"})
        )

        mock_get_selectors.assert_called_once_with(build_origin=["legacy"])
