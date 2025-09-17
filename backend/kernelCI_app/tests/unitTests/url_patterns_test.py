from django.urls import reverse, resolve


class TestURLPatterns:
    def test_simple_git_branch_direct_patterns(self):
        """Test simple git branch direct patterns."""
        git_branch = "master"
        tree_name = "mainline"
        commit_hash = "abc123"

        patterns = [
            "treeCommitsDirectView",
            "treeDetailsBootsDirectView",
            "treeDetailsBuildsDirectView",
            "treeDetailsDirectView",
            "treeDetailsDirectSummaryView",
            "treeDetailsTestsDirectView",
        ]

        for pattern in patterns:
            url = reverse(
                pattern,
                kwargs={
                    "tree_name": tree_name,
                    "git_branch": git_branch,
                    "commit_hash": commit_hash,
                },
            )
            resolved = resolve(url)
            assert resolved.url_name == pattern
            assert resolved.kwargs["tree_name"] == tree_name
            assert resolved.kwargs["git_branch"] == git_branch
            assert resolved.kwargs["commit_hash"] == commit_hash

    def test_direct_tree_patterns_with_complex_branches(self):
        """Test patterns with complex branch names containing slashes."""
        tree_name = "soc"
        git_branch = "arm/fixes"
        commit_hash = "fake-commit-hash"

        patterns = [
            "treeCommitsDirectView",
            "treeDetailsBootsDirectView",
            "treeDetailsBuildsDirectView",
            "treeDetailsDirectView",
            "treeDetailsDirectSummaryView",
            "treeDetailsTestsDirectView",
        ]

        for pattern in patterns:
            url = reverse(
                pattern,
                kwargs={
                    "tree_name": tree_name,
                    "git_branch": git_branch,
                    "commit_hash": commit_hash,
                },
            )

            resolved = resolve(url)
            assert resolved.url_name == pattern
            assert resolved.kwargs["tree_name"] == tree_name
            assert resolved.kwargs["git_branch"] == git_branch
            assert resolved.kwargs["commit_hash"] == commit_hash

    def test_url_parsing_with_summary(self):
        """Test url parsing with summary."""
        test_url = "/api/tree/soc/arm/fixes/fake-commit-hash/summary"
        resolved = resolve(test_url)

        assert resolved.url_name == "treeDetailsDirectSummaryView"
        assert resolved.kwargs["tree_name"] == "soc"
        assert resolved.kwargs["git_branch"] == "arm/fixes"
        assert resolved.kwargs["commit_hash"] == "fake-commit-hash"

    def test_simple_git_branch_tree_latest(self):
        """Test that treeLatest works correctly with simple branch names."""
        tree_name = "mainline"
        git_branch = "master"

        url = reverse(
            "treeLatest",
            kwargs={
                "tree_name": tree_name,
                "git_branch": git_branch,
            },
        )
        resolved = resolve(url)
        assert resolved.url_name == "treeLatest"
        assert resolved.kwargs["tree_name"] == tree_name
        assert resolved.kwargs["git_branch"] == git_branch

    def test_tree_latest_with_complex_branches(self):
        """Test that treeLatest works correctly with complex branch names."""
        tree_name = "soc"
        git_branch = "arm/fixes"

        url = reverse(
            "treeLatest",
            kwargs={
                "tree_name": tree_name,
                "git_branch": git_branch,
            },
        )
        resolved = resolve(url)
        assert resolved.url_name == "treeLatest"
        assert resolved.kwargs["tree_name"] == tree_name
        assert resolved.kwargs["git_branch"] == git_branch

    def test_ids_tree_url_patterns(self):
        url = reverse("testDetails", kwargs={"test_id": "test123"})
        resolved = resolve(url)
        assert resolved.url_name == "testDetails"
        assert resolved.kwargs["test_id"] == "test123"

        url = reverse("buildDetails", kwargs={"build_id": "build456"})
        resolved = resolve(url)
        assert resolved.url_name == "buildDetails"
        assert resolved.kwargs["build_id"] == "build456"

        url = reverse("hardwareDetails", kwargs={"hardware_id": "hw789"})
        resolved = resolve(url)
        assert resolved.url_name == "hardwareDetails"
        assert resolved.kwargs["hardware_id"] == "hw789"

    def test_tree_commit_hash_patterns(self):
        commit_hash = "1234567890abcdef"

        url = reverse("treeDetailsView", kwargs={"commit_hash": commit_hash})
        resolved = resolve(url)
        assert resolved.kwargs["commit_hash"] == commit_hash

        url = reverse("treeDetailsSummaryView", kwargs={"commit_hash": commit_hash})
        resolved = resolve(url)
        assert resolved.kwargs["commit_hash"] == commit_hash
