import argparse
import datetime as dt
import re
from pathlib import Path


VALID_TYPES = {
    "Concepts": "concept",
    "Methods": "method",
    "Projects": "project",
    "Workflows": "workflow",
    "Media": "media",
}


TEMPLATES = {
    "Concepts": ["一句话定义", "核心问题", "关键机制", "使用场景", "与相关概念的区别", "我的理解", "Source"],
    "Methods": ["适用场景", "核心步骤", "判断标准", "常见误区", "示例", "Source"],
    "Projects": ["项目是什么", "解决什么问题", "关键设计", "可借鉴点", "Source"],
    "Workflows": ["目标", "输入", "流程", "输出", "检查点", "Source"],
    "Media": ["媒体信息", "核心内容", "值得回看的部分", "Source"],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def slugify(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|#^\[\]]+', "", name).strip()
    return name[:90] or "Knowledge"


def wiki_link(vault: Path, path: Path) -> str:
    return path.resolve().relative_to(vault.resolve()).with_suffix("").as_posix()


def split_frontmatter(text: str) -> tuple[str, str, str]:
    if not text.startswith("---\n"):
        return "", "", text
    end = text.find("\n---", 4)
    if end == -1:
        return "", "", text
    return text[:4], text[4:end].strip(), text[end + 4 :].lstrip()


def add_knowledge_to_frontmatter(text: str, knowledge_ref: str) -> str:
    start, fm, body = split_frontmatter(text)
    if not fm:
        fm = f"knowledge_links:\n  - \"[[{knowledge_ref}]]\""
        return f"---\n{fm}\n---\n\n{text}"

    if "knowledge_links:" not in fm:
        fm = fm + f"\nknowledge_links:\n  - \"[[{knowledge_ref}]]\""
    elif f"[[{knowledge_ref}]]" not in fm:
        fm = re.sub(r"knowledge_links:\s*\[\]", f"knowledge_links:\n  - \"[[{knowledge_ref}]]\"", fm)
        if f"[[{knowledge_ref}]]" not in fm:
            fm = re.sub(r"(knowledge_links:\n(?:  - .+\n?)*)", rf"\1  - \"[[{knowledge_ref}]]\"\n", fm, count=1)
    return f"---\n{fm}\n---\n\n{body}"


def add_linked_knowledge_section(text: str, knowledge_ref: str) -> str:
    bullet = f"- [[{knowledge_ref}]]"
    if bullet in text:
        return text
    pattern = re.compile(r"(^## Linked Knowledge\s*$)([\s\S]*?)(?=^##\s+|\Z)", re.M)
    match = pattern.search(text)
    if not match:
        return text.rstrip() + f"\n\n## Linked Knowledge\n\n{bullet}\n"
    section = match.group(2).strip()
    if not section or section == "-":
        replacement = match.group(1) + "\n\n" + bullet + "\n\n"
    else:
        replacement = match.group(1) + "\n\n" + section + "\n" + bullet + "\n\n"
    return text[: match.start()] + replacement + text[match.end() :]


def knowledge_template(title: str, kind: str, source_ref: str) -> str:
    created = dt.date.today().isoformat()
    note_type = VALID_TYPES[kind]
    lines = [
        "---",
        f'title: "{title.replace(chr(34), chr(39))}"',
        f"created: {created}",
        f"type: {note_type}",
        "status: draft",
        "tags:",
        f"  - knowledge/{note_type}",
        "sources:",
        f"  - \"[[{source_ref}]]\"",
        "related: []",
        "---",
        "",
        f"# {title}",
        "",
    ]
    for heading in TEMPLATES[kind]:
        lines.extend([f"## {heading}", ""])
        if heading == "Source":
            lines.extend([f"- [[{source_ref}]]", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Knowledge note and link it with a Source note.")
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault.")
    parser.add_argument("--source", required=True, help="Path to the Source note.")
    parser.add_argument("--type", required=True, choices=sorted(VALID_TYPES), help="Knowledge folder/type.")
    parser.add_argument("--title", required=True, help="Knowledge note title.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing Knowledge note.")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    source_path = Path(args.source).expanduser().resolve()
    if not source_path.exists():
        raise SystemExit(f"Source file does not exist: {source_path}")

    knowledge_path = vault / "20_Knowledge" / args.type / f"{slugify(args.title)}.md"
    source_ref = wiki_link(vault, source_path)
    knowledge_ref = wiki_link(vault, knowledge_path)

    if knowledge_path.exists() and not args.overwrite:
        print(f"knowledge_exists={knowledge_path}")
    else:
        write_text(knowledge_path, knowledge_template(args.title, args.type, source_ref))
        print(f"knowledge_created={knowledge_path}")

    source_text = read_text(source_path)
    source_text = add_knowledge_to_frontmatter(source_text, knowledge_ref)
    source_text = add_linked_knowledge_section(source_text, knowledge_ref)
    write_text(source_path, source_text)
    print(f"source_updated={source_path}")
    print(f"knowledge_ref={knowledge_ref}")


if __name__ == "__main__":
    main()
