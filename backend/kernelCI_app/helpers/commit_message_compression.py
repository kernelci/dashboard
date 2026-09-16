def message_to_bytea(plain: str | None) -> bytes | None:
    if plain is None:
        return None
    return plain.encode("utf-8")


def bytea_to_message(data: bytes | memoryview | None) -> str | None:
    if data is None:
        return None
    raw = bytes(data)
    if not raw:
        return None
    return raw.decode("utf-8")
