from http import HTTPStatus
from kernelCI_app.typeModels.hardwareDetails import HardwareDetailsPostBody
import copy


UNEXISTENT_HARDWARE_ID = {
    "id": "no hardware id",
    "body": HardwareDetailsPostBody(
        origin="",
        startTimestampInSeconds=1737487800,
        endTimestampInSeconds=1737574200,
        selectedCommits={},
        filter={},
    ),
}

BAD_REQUEST_REQUEST_BODY = {
    "id": "google,juniper",
    "body": HardwareDetailsPostBody(
        origin="",
        startTimestampInSeconds="",
        endTimestampInSeconds="",
        selectedCommits={},
        filter={},
    ),
}

GOOGLE_JUNIPER_HARDWARE_WITHOUT_FILTERS = {
    "id": "google,juniper",
    "body": HardwareDetailsPostBody(
        startTimestampInSeconds=1740227400,
        endTimestampInSeconds=1740659400,
        selectedCommits={},
        filter={},
    ),
}

ARM_JUNO_HARDWARE_WITHOUT_FILTERS = {
    "id": "arm,juno",
    "body": HardwareDetailsPostBody(
        startTimestampInSeconds=1740232800,
        endTimestampInSeconds=1740664800,
        selectedCommits={},
        filter={},
    ),
}

GOOGLE_JUNIPER_HARDWARE_WITH_FILTERS = copy.deepcopy(
    GOOGLE_JUNIPER_HARDWARE_WITHOUT_FILTERS
)
GOOGLE_JUNIPER_HARDWARE_WITH_FILTERS["body"].filter = {
    "filter_architecture": ["arm64"],
    "filter_boot.status": ["PASS"],
}

HARDWARE_WITH_UNEXISTENT_FILTER_VALUE = copy.deepcopy(
    GOOGLE_JUNIPER_HARDWARE_WITHOUT_FILTERS
)
HARDWARE_WITH_UNEXISTENT_FILTER_VALUE["body"].filter = {
    "filter_architecture": ["invalid"]
}

HARDWARE_WITH_GLOBAL_FILTER = {
    "id": "aaeon-UPN-EHLX4RE-A10-0864",
    "body": HardwareDetailsPostBody(
        startTimestampInSeconds=1740241800,
        endTimestampInSeconds=1740673800,
        selectedCommits={},
        filter={
            "filter_architecture": ["i386"],
            "filter_config_name": ["defconfig"],
            "filter_compiler": ["gcc-12"],
            "filter_valid": ["true"],
        },
    ),
}

# https://staging.dashboard.kernelci.org:9000/hardware/allwinner%2Csun50i-a64?et=1741881600&st=1741449600
ALLWINNER_HARDWARE = {
    "id": "allwinner,sun50i-a64",
    "body": HardwareDetailsPostBody(
        origin="maestro",
        startTimestampInSeconds=1741449600,
        endTimestampInSeconds=1741881600,
        selectedCommits={
            "0": "5b4ec6e1eb7603b6d86a172d77efdf75eb741e7e",
            "1": "head",
            "4": "0704a15b930cf97073ce091a0cd7ad32f2304329",
        },
        filter={},
    ),
}

SUCCESS_EXPECTED_RESPONSE = {
    "expected_status": HTTPStatus.OK,
    "has_error": False,
    "check_emptiness": False,
}

ERROR_EXPECTED_RESPONSE = {
    "expected_status": HTTPStatus.OK,
    "has_error": True,
    "check_emptiness": False,
}

BAD_REQUEST_EXPECTED_RESPONSE = {
    "expected_status": HTTPStatus.BAD_REQUEST,
    "has_error": True,
    "check_emptiness": False,
}

EMPTY_EXPECTED_RESPONSE = {
    "expected_status": HTTPStatus.OK,
    "has_error": False,
    "check_emptiness": True,
}
