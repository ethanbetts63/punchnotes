"""Small validation helpers shared by line and beat validators."""


def positive_int(value) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def sequential_error(label: str, numbers: set[int]) -> str | None:
    if not numbers:
        return None
    expected = set(range(1, max(numbers) + 1))
    if numbers == expected:
        return None
    missing = ", ".join(str(n) for n in sorted(expected - numbers))
    actual = ", ".join(str(n) for n in sorted(numbers))
    return f"{label}: numbers must be sequential starting at 1; got [{actual}], missing [{missing}]"


def is_non_empty_string(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


