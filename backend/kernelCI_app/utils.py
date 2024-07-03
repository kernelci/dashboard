def get_visible_records(table_name):
    return visible_records.get(table_name, {})


def get_visible_record_ids(table_name):
    return list(get_visible_records(table_name).keys())


def get_visible_record_config(table_name, id):
    return get_visible_records(table_name).get(id)


visible_records = {
    "checkouts": {
        "broonie:7592653346c84691a16ccd1c115df05c": {
            "tree_name": "mainline",
            "build_status": {"finished": 160, "total": 182},
            "test_status": {"finished": 182, "total": 182},
        },
        "broonie:170e93ec1178448293bb3b1163b1a4ee": {
            "tree_name": "stable",
            "build_status": {"finished": 182, "total": 182},
            "test_status": {"finished": 820, "total": 820},
        },
        "broonie:88964264010d43159ffa28bb524be058": {
            "tree_name": "stable",
            "build_status": {"finished": 160, "total": 182},
            "test_status": {"finished": 642, "total": 820}
        },
        "broonie:12f55b2668fb4eca9254bfadad4ee871": {
            "tree_name": "stable",
            "build_status": {"finished": 182, "total": 182},
            "test_status": {"finished": 820, "total": 820}
        },
        "broonie:c4ea3368208f4909b5af51c6a148047d": {
            "tree_name": "stable",
            "build_status": {"finished": 182, "total": 182},
            "test_status": {"finished": 820, "total": 820}
        },
        "broonie:1b17e613a3e94254af6fef1167572d35": {
            "tree_name": "stable",
            "build_status": {"finished": 182, "total": 182},
            "test_status": {"finished": 820, "total": 820}
        },
    }
}
