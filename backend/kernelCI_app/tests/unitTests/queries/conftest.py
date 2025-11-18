from unittest.mock import MagicMock, Mock

from kernelCI_app.typeModels.hardwareDetails import Tree


def setup_mock_cursor(mock_connection):
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_cursor


def setup_mock_queryset(mock_model, return_value):
    mock_queryset = Mock()
    mock_queryset.values.return_value = mock_queryset
    mock_queryset.filter.return_value = mock_queryset
    mock_queryset.order_by.return_value = mock_queryset
    mock_queryset.first.return_value = return_value
    mock_model.objects.values.return_value = mock_queryset
    return mock_queryset


def setup_mock_test_queryset(mock_tests_model):
    mock_queryset = Mock()
    mock_queryset.values.return_value = mock_queryset
    mock_queryset.filter.return_value = mock_queryset
    mock_queryset.order_by.return_value = mock_queryset
    mock_sliced = Mock()
    mock_sliced.__iter__ = Mock(return_value=iter([]))
    mock_queryset.__getitem__ = Mock(return_value=mock_sliced)
    mock_tests_model.objects.filter.return_value = mock_queryset
    return mock_queryset


TEST_TREE = Tree(
    index="0",
    tree_name="mainline",
    origin="maestro",
    git_repository_branch="master",
    git_repository_url="https://my_url.com",
    head_git_commit_name="v6.1",
    head_git_commit_hash="abc123",
    head_git_commit_tag=None,
    selected_commit_status=None,
    is_selected=None,
)


def setup_mock_query_builder(mock_query_class, return_value):
    mock_query = Mock()
    mock_query.from_table.return_value = mock_query
    mock_query.join.return_value = mock_query
    mock_query.where.return_value = mock_query
    mock_query.select.return_value = return_value
    mock_query_class.return_value = mock_query
    return mock_query


def setup_mock_filter_values_queryset(mock_model, return_value):
    mock_filter_queryset = Mock()
    mock_filter_queryset.annotate.return_value = mock_filter_queryset
    mock_filter_queryset.values.return_value = return_value
    mock_model.objects.filter.return_value = mock_filter_queryset
    return mock_filter_queryset
