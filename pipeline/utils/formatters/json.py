import json


def reorder(data: dict, order: list[str]) -> dict:
    out = {key: data[key] for key in order if key in data}
    out.update({key: value for key, value in data.items() if key not in out})
    return out


def compact_lines(field_order: list[str]):
    def fmt(lines):
        inner = []
        for index, line in enumerate(lines):
            comma = "," if index < len(lines) - 1 else ""
            inner.append(f"    {json.dumps(reorder(line, field_order), ensure_ascii=False)}{comma}")
        return "[\n" + "\n".join(inner) + "\n  ]"

    return fmt


def dump_object(items, handlers=None) -> str:
    default = lambda value: json.dumps(value, ensure_ascii=False)
    handlers = handlers or {}
    rows = ["{\n"]
    entries = list(items)
    for index, (key, value) in enumerate(entries):
        comma = "," if index < len(entries) - 1 else ""
        rows.append(f"  {json.dumps(key)}: {handlers.get(key, default)(value)}{comma}\n")
    rows.append("}\n")
    return "".join(rows)
