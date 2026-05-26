import hashlib

SELECTED_HEAD_TREE_VALUE = "head"
TREE_KEY_HASH_LENGTH = 14


def make_tree_key(tree_name: str, branch: str, url: str) -> str:
    raw = f"{tree_name}|{branch}|{url}"
    return hashlib.sha256(raw.encode()).hexdigest()[:TREE_KEY_HASH_LENGTH]
