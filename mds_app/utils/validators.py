def compare_headers(existing, incoming):
    return {
        "missing": list(set(existing) - set(incoming)),
        "extra": list(set(incoming) - set(existing))
    }
