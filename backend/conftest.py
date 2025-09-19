import tomllib
from pytest import Item
import os
import django
from django.conf import settings


def pytest_addoption(parser):
    parser.addoption(
        "--run-all", action="store_true", default=False, help="run all test cases"
    )
    parser.addoption(
        "--use-local-db",
        action="store_true",
        default=False,
        help="use local test database instead of remote",
    )


def pytest_configure(config):
    """Configure Django settings for tests."""
    if not settings.configured:
        use_local_db = config.getoption("--use-local-db")

        if use_local_db:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kernelCI.test_settings")
        else:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kernelCI.settings")

        django.setup()


def get_test_markers() -> list[str]:
    try:
        pyproject_path = os.path.join(os.path.dirname(__file__), "pyproject.toml")

        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        markers: list[str] = (
            pyproject_data.get("tool", {})
            .get("pytest", {})
            .get("ini_options", {})
            .get("markers", [])
        )

        marker_names = []
        for marker in markers:
            if ":" in marker:
                marker_name = marker.split(":")[0].strip()
                marker_names.append(marker_name)

        if not marker_names:
            raise ValueError("No markers found in pyproject.toml")

        return marker_names

    except FileNotFoundError:
        raise FileNotFoundError("pyproject.toml not found")
    except Exception as e:
        raise e(f"Error reading markers from pyproject.toml: {e}")


def pytest_collection_modifyitems(items: list[Item]):
    test_markers = get_test_markers()

    for item in items:
        parent_folder = item.path.parent.name.lower()

        matched_markers = [marker for marker in test_markers if marker in parent_folder]
        match len(matched_markers):
            case 0:
                raise Exception(
                    """Test %s must have a type.
                    Place the test in a folder whose name contains 'unit' or 'integration'."""
                    % item.name
                )
            case 1:
                item.add_marker(matched_markers[0])
            case _:
                raise Exception(
                    """Test %s can only be of a single type (one of %s),
                        but found multiple markers (%s) at folder %s"""
                    % (
                        item.name,
                        test_markers,
                        matched_markers,
                        parent_folder,
                    )
                )
