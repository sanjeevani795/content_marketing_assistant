from pathlib import Path


def export_markdown(content: str, output_path: str) -> str:
    path = Path(output_path)
    path.write_text(content, encoding="utf-8")
    return str(path)
