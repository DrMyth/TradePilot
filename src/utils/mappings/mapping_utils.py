def to_code(value, mapping):
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        return mapping.get(value.upper())
    return None