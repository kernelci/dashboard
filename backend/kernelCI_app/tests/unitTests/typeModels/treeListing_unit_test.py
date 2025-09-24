from datetime import datetime
from kernelCI_app.typeModels.treeListing import (
    TestStatusCount,
    Checkout,
)
from kernelCI_app.typeModels.common import StatusCount


class TestCheckout:
    """Test cases for Checkout class."""

    def test_checkout_creation(self):
        """Test Checkout with all fields."""
        build_status = StatusCount(PASS=5, FAIL=1)
        test_status = TestStatusCount(
            **{"pass": 3}, error=0, fail=1, skip=0, miss=0, done=0, null=0
        )
        boot_status = TestStatusCount(
            **{"pass": 2}, error=1, fail=0, skip=0, miss=0, done=0, null=0
        )
        tags = [["tag1"], ["tag2"]]

        checkout = Checkout(
            git_repository_url="https://git.example.com/repo",
            git_commit_hash="ghi789",
            git_commit_name="commit_name3",
            origin="origin3",
            git_repository_branch="develop",
            start_time="2023-01-01T00:00:00",
            origin_builds_finish_time="2023-01-01T01:00:00",
            origin_tests_finish_time="2023-01-01T02:00:00",
            checkout_id="checkout123",
            build_status=build_status,
            test_status=test_status,
            boot_status=boot_status,
            tree_name="tree1",
            git_commit_tags=tags,
        )

        assert checkout.git_repository_url == "https://git.example.com/repo"
        assert checkout.git_commit_hash == "ghi789"
        assert checkout.git_commit_name == "commit_name3"
        assert checkout.origin == "origin3"
        assert checkout.git_repository_branch == "develop"
        assert checkout.start_time == datetime(2023, 1, 1, 0, 0)
        assert checkout.origin_builds_finish_time == datetime(2023, 1, 1, 1, 0)
        assert checkout.origin_tests_finish_time == datetime(2023, 1, 1, 2, 0)
        assert checkout.id == "checkout123"
        assert checkout.build_status == build_status
        assert checkout.test_status == test_status
        assert checkout.boot_status == boot_status
        assert checkout.tree_name == "tree1"
        assert checkout.git_commit_tags == tags

    def test_checkout_add_counts(self):
        """Test add_counts method."""
        checkout = Checkout(
            git_repository_url="https://git.example.com/repo",
            git_commit_hash="jkl012",
            git_commit_name="commit_name4",
            origin="origin4",
            git_repository_branch="feature",
            start_time="2023-01-01T00:00:00",
            origin_builds_finish_time="2023-01-01T01:00:00",
            origin_tests_finish_time="2023-01-01T02:00:00",
            checkout_id="checkout456",
            build_status=StatusCount(PASS=2, FAIL=1),
            test_status=TestStatusCount(
                **{"pass": 1}, error=0, fail=1, skip=0, miss=0, done=0, null=0
            ),
            boot_status=TestStatusCount(
                **{"pass": 1}, error=1, fail=0, skip=0, miss=0, done=0, null=0
            ),
            tree_name="tree2",
            git_commit_tags=[["tag3"]],
        )

        additional_build_status = StatusCount(PASS=1, ERROR=1)
        additional_test_status = TestStatusCount(
            **{"pass": 2}, error=0, fail=0, skip=1, miss=0, done=0, null=0
        )
        additional_boot_status = TestStatusCount(
            **{"pass": 1}, error=0, fail=0, skip=0, miss=0, done=0, null=1
        )

        checkout.add_counts(
            additional_build_status, additional_test_status, additional_boot_status
        )

        assert checkout.build_status.PASS == 3
        assert checkout.build_status.FAIL == 1
        assert checkout.build_status.ERROR == 1

        assert checkout.test_status.pass_count == 3
        assert checkout.test_status.fail_count == 1
        assert checkout.test_status.skip_count == 1

        assert checkout.boot_status.pass_count == 2
        assert checkout.boot_status.error_count == 1
        assert checkout.boot_status.null_count == 1
