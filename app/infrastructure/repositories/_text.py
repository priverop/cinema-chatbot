import unicodedata


def fold(value: str | None) -> str:
    if not value:
        return ""
    nfkd = unicodedata.normalize("NFKD", value)
    stripped = "".join(c for c in nfkd if not unicodedata.combining(c))
    return stripped.casefold()
