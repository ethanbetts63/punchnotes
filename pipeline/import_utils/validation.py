PREMISE_STRUCTURE_RULES: dict[str, tuple[str, ...]] = {
    "misdirect": ("implies", "but"),
    "reframe": ("could be",),
    "phonetic-match": ("sounds like", "and"),
    "double-meaning": ("can mean", "or"),
    "analogy": ("is like", "because both"),
    "hyperbole": ("so", "that"),
    "elephant-in-the-room": ("widely understood", "but rarely"),
}

VALID_JOKE_TYPES = frozenset(PREMISE_STRUCTURE_RULES)


def validate_bit_meta(meta: dict) -> None:
    """Raises ValueError if any beat has an invalid joke_type or malformed premise."""
    errors = []
    for bit_num, bit_data in meta.get("bit_meta", {}).items():
        for beat_num, beat_data in bit_data.get("beats", {}).items():
            location = f"bit {bit_num} beat {beat_num}"
            joke_type = beat_data.get("joke_type")
            premise = beat_data.get("premise")

            if joke_type not in PREMISE_STRUCTURE_RULES:
                accepted = ", ".join(sorted(PREMISE_STRUCTURE_RULES))
                errors.append(
                    f"{location}: joke_type must be one of [{accepted}], got {joke_type!r}"
                )
                continue

            if not isinstance(premise, str) or not premise.strip():
                errors.append(f"{location}: premise is required for joke_type {joke_type!r}")
                continue

            missing = [
                phrase
                for phrase in PREMISE_STRUCTURE_RULES[joke_type]
                if phrase not in premise.lower()
            ]
            if missing:
                required = ", ".join(f'"{p}"' for p in PREMISE_STRUCTURE_RULES[joke_type])
                errors.append(
                    f"{location}: {joke_type} premise must contain {required}; "
                    f"missing {', '.join(repr(p) for p in missing)}"
                )

    if errors:
        raise ValueError("Invalid bit_meta:\n  " + "\n  ".join(errors))
