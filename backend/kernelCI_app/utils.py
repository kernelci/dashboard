def get_visible_records(table_name):
    return visible_records.get(table_name, {})


def get_visible_record_identifiers(table_name):
    return list(get_visible_records(table_name).keys())


def get_visible_record_config(table_name, id):
    return get_visible_records(table_name).get(id)


visible_records = {
    "checkouts": {
        "22a40d14b572deb80c0648557f4bd502d7e83826": {
            "tree_name": "mainline",
            "git_repository_branch": "master",
            "git_commit_name": "v6.10-rc6"
        },
        "61945f2f69d080a9cf2c879cb959d4648df9b94c": {
            "tree_name": "stable",
            "git_repository_branch": "linux-6.6.y",
            "git_commit_name": "v6.6.36"
        },
        "99e6a620de00b96f059c9e7f14b5795ca0c6b125": {
            "tree_name": "stable",
            "git_repository_branch": "linux-6.1.y",
            "git_commit_name": "v6.1.96"
        },
        "4878aadf2d1519f3731ae300ce1fef78fc63ee30": {
            "tree_name": "stable",
            "git_repository_branch": "linux-5.15.y",
            "git_commit_name": "v5.15.161"
        },
        "3a3877de44342d0a09216dfbe674a404e8f5e96f": {
            "tree_name": "stable",
            "git_repository_branch": "linux-5.10.y",
            "git_commit_name": "v5.10.220"
        },
        "189ee9735a4b2e8095b1a6c088ebc8e133872471": {
            "tree_name": "stable",
            "git_repository_branch": "linux-5.4.y",
            "git_commit_name": "v5.4.278"
        },
        "b37477f5316fe37f74645a5d9d92a3a9c93d8cfa": {
            "tree_name": "stable",
            "git_repository_branch": "linux-4.19.y",
            "git_commit_name": "v4.19.316"
        },
    }
}
