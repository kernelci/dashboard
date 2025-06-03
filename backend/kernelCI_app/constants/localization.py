# This file implements a rough start for localization,
# but it doesn't implement the entire localization system.

from enum import StrEnum, _simple_enum


# TODO: replace this enum with a proper localization system
@_simple_enum(StrEnum)
class ClientStrings:
    """Simple class for storing basis for internationalization strings"""

    TREE_BUILDS_NOT_FOUND = "No builds available for this tree/branch/commit"
    TREE_BOOTS_NOT_FOUND = "No boots available for this tree/branch/commit"
    TREE_NOT_FOUND = "No results available for this tree/branch/commit"
    TREE_TESTS_NOT_FOUND = "No tests available for this tree/branch/commit"
