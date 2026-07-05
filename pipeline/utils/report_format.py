import json


def format_report_json(obj, level: int = 0) -> str:
    pad = "  " * level
    inner = "  " * (level + 1)
    if isinstance(obj, dict):
        if set(obj.keys()) <= {"label", "text"}:
            return json.dumps(obj, ensure_ascii=False)
        items = [f'{inner}{json.dumps(k)}: {format_report_json(v, level + 1)}' for k, v in obj.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(obj, list):
        if all(isinstance(x, str) for x in obj):
            return json.dumps(obj, ensure_ascii=False)
        items = [f'{inner}{format_report_json(v, level + 1)}' for v in obj]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    return json.dumps(obj, ensure_ascii=False)
