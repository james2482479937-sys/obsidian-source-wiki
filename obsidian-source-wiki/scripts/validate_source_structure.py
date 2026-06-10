import argparse
import re
import sys
from pathlib import Path


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


GENERIC_HEADINGS = {
    "视频转录",
    "Transcript",
    "图片 OCR",
    "Image content (OCR)",
    "内容",
    "Notes",
    "作者原始描述",
}
IGNORED_HEADINGS = {
    "Source Info",
    "Structure Tags",
    "Linked Knowledge",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def frontmatter_value(md: str, key: str) -> str:
    if not md.startswith("---\n"):
        return ""
    end = md.find("\n---", 4)
    if end == -1:
        return ""
    for line in md[4:end].splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip('"')
    return ""


def h2_headings(md: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"^##\s+(.+)$", md, flags=re.M)]


def long_paragraphs(md: str, max_chars: int) -> list[int]:
    lines = md.splitlines()
    paragraphs = []
    start = 1
    current = []
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("---") or stripped.startswith("- "):
            if current:
                paragraphs.append((start, " ".join(current)))
                current = []
            start = index + 1
            continue
        if not current:
            start = index
        current.append(stripped)
    if current:
        paragraphs.append((start, " ".join(current)))
    return [line for line, text in paragraphs if len(text) > max_chars]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate that a Source note has semantic structure, not only raw transcript paragraphs.")
    parser.add_argument("--source", required=True, help="Path to a Source markdown file.")
    parser.add_argument("--min-semantic-headings", type=int, default=3)
    parser.add_argument("--max-paragraph-chars", type=int, default=900)
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    md = read_text(source)
    errors = []

    status = frontmatter_value(md, "status")
    if status != "source_structured":
        errors.append("frontmatter status must be source_structured")

    headings = h2_headings(md)
    generic = [heading for heading in headings if heading in GENERIC_HEADINGS or re.match(r"^(片段|段落|Part)\s*\d+", heading, re.I)]
    if generic:
        errors.append("generic headings are not allowed: " + ", ".join(generic))

    semantic = [heading for heading in headings if heading not in IGNORED_HEADINGS and heading not in GENERIC_HEADINGS]
    if len(semantic) < args.min_semantic_headings:
        errors.append(f"need at least {args.min_semantic_headings} semantic H2 headings; found {len(semantic)}")

    long_lines = long_paragraphs(md, args.max_paragraph_chars)
    if long_lines:
        errors.append("paragraphs too long near line(s): " + ", ".join(str(line) for line in long_lines[:8]))

    if errors:
        print("source_structure=failed")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("source_structure=ok")
    print(f"semantic_headings={len(semantic)}")
    print(f"source={source}")


if __name__ == "__main__":
    main()
