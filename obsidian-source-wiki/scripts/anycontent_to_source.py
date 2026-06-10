import argparse
import datetime as dt
import re
import sys
import time
from pathlib import Path


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


SUPPORTED_URL = re.compile(
    r"https?://(?:v\.douyin\.com|www\.douyin\.com|www\.iesdouyin\.com|"
    r"www\.tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com|"
    r"mp\.weixin\.qq\.com|www\.youtube\.com|youtube\.com|youtu\.be|m\.youtube\.com)"
    r"[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+",
    re.I,
)


def today() -> str:
    return dt.date.today().isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_urls(text: str) -> list[str]:
    urls = []
    for match in SUPPORTED_URL.finditer(text):
        url = match.group(0).rstrip(".,;，。；!?)）")
        if url not in urls:
            urls.append(url)
    return urls


def raw_snapshot(raw_dir: Path) -> dict[Path, float]:
    if not raw_dir.exists():
        return {}
    return {p: p.stat().st_mtime for p in raw_dir.rglob("*.md") if p.is_file()}


def wait_for_new_raw(raw_dir: Path, before: dict[Path, float], timeout: int) -> Path:
    deadline = time.time() + timeout
    while time.time() < deadline:
        candidates = []
        for path in raw_dir.rglob("*.md") if raw_dir.exists() else []:
            mtime = path.stat().st_mtime
            if path not in before or mtime > before.get(path, 0):
                candidates.append((mtime, path))
        if candidates:
            candidates.sort(reverse=True)
            time.sleep(1)
            return candidates[0][1]
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for AnyContent raw output after {timeout} seconds.")


def submit_to_inbox(inbox_dir: Path, share_text: str, label: str) -> Path:
    inbox_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(label)}.md"
    path = inbox_dir / filename
    write_text(path, share_text.strip() + "\n")
    return path


def parse_frontmatter(md: str) -> tuple[dict[str, str], str]:
    if not md.startswith("---\n"):
        return {}, md
    end = md.find("\n---", 4)
    if end == -1:
        return {}, md
    raw = md[4:end].strip()
    body = md[end + 4 :].lstrip()
    data: dict[str, str] = {}
    current_key = None
    for line in raw.splitlines():
        if re.match(r"^[A-Za-z0-9_\-]+:", line):
            key, value = line.split(":", 1)
            current_key = key.strip()
            data[current_key] = value.strip().strip('"')
        elif current_key:
            data[current_key] += "\n" + line.rstrip()
    return data, body


def section(md: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)", re.M)
    match = pattern.search(md)
    return match.group(1).strip() if match else ""


def first_h1(md: str) -> str:
    match = re.search(r"^#\s+(.+)$", md, re.M)
    return match.group(1).strip() if match else "Untitled"


def author_from_frontmatter(value: str) -> str:
    match = re.search(r"\[\[(.*?)\]\]", value or "")
    if match:
        return match.group(1)
    return re.sub(r"^-\s*", "", value or "").strip()


def clean_markdown(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def paragraphize_transcript(text: str, max_chars: int = 280) -> str:
    text = re.sub(r"\s+", "", text).strip()
    if not text:
        return ""
    parts = re.split(r"(?<=[。！？!?])", text)
    paragraphs = []
    current = ""
    for part in parts:
        if not part:
            continue
        if current and len(current) + len(part) > max_chars:
            paragraphs.append(current)
            current = part
        else:
            current += part
    if current:
        paragraphs.append(current)
    return "\n\n".join(paragraphs)


def slugify(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|#^\[\]]+', "", name)
    name = re.sub(r"\s+", "-", name).strip("- .")
    return name[:80] or "source"


def build_source(vault: Path, raw_path: Path, raw_md: str, capture_path: Path | None) -> tuple[str, str]:
    fm, body = parse_frontmatter(raw_md)
    title = fm.get("title") or first_h1(body)
    platform = fm.get("platform") or "unknown"
    source_type = fm.get("source_type") or fm.get("post_type") or "unknown"
    source_url = fm.get("source") or ""
    author = author_from_frontmatter(fm.get("author", ""))
    created = today()
    saved_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    raw_rel = raw_path.relative_to(vault).with_suffix("").as_posix()

    description = section(body, "Description") or section(body, "Original caption")
    transcript = section(body, "Transcript")
    image_ocr = section(body, "Image content (OCR)")

    lines = [
        "---",
        f'title: "{title.replace(chr(34), chr(39))}"',
        f"created: {created}",
        f"source_type: {source_type}",
        f"platform: {platform}",
        f'author: "{author.replace(chr(34), chr(39))}"',
        f"source_url: {source_url}",
        f"saved_at: {saved_at}",
        "status: source_draft",
        "tags:",
        f"  - source/{source_type}",
        f"  - platform/{platform}",
        "knowledge_links: []",
        "---",
        "",
        f"# {title}",
        "",
        "> Draft only. This Source is not complete until an agent rewrites it with semantic headings and `status: source_structured`.",
        "",
        "## Source Info",
        "",
        f"- 平台：{platform}",
        f"- 作者：{author or '未知'}",
        f"- 原链接：{source_url}",
        f"- AnyContent 原始文件：[[{raw_rel}]]",
    ]
    if capture_path:
        try:
            capture_rel = capture_path.relative_to(vault).with_suffix("").as_posix()
            lines.append(f"- Capture 来源：[[{capture_rel}]]")
        except ValueError:
            lines.append(f"- Capture 来源：{capture_path}")
    lines.extend(["", "## 作者原始描述", "", clean_markdown(description) or "（无描述）", ""])

    if transcript:
        lines.extend(["## 视频转录", "", paragraphize_transcript(transcript), ""])
    if image_ocr:
        lines.extend(["## 图片 OCR", "", clean_markdown(image_ocr), ""])
    if not transcript and not image_ocr:
        lines.extend(["## 内容", "", "（无转录或 OCR 内容）", ""])

    lines.extend(
        [
            "## Structure Tags",
            "",
            "- 主题：",
            "- 人物：",
            "- 概念：",
            "- 场景：",
            "",
            "## Linked Knowledge",
            "",
            "- ",
            "",
        ]
    )
    return title, "\n".join(lines)


def selected_share_text(full_text: str, selected_url: str) -> str:
    for line in full_text.splitlines():
        if selected_url in line:
            return line
    return selected_url


def process_one(vault: Path, share_text: str, capture_path: Path | None, index: int, timeout: int, write: bool) -> Path:
    urls = extract_urls(share_text)
    if not urls:
        raise SystemExit("No AnyContent-supported URL found.")
    if index < 0 or index >= len(urls):
        raise SystemExit(f"--index out of range. Found {len(urls)} supported URLs.")

    selected_url = urls[index]
    selected_text = selected_share_text(share_text, selected_url)
    raw_dir = vault / "_System" / "AnyContent" / "raw"
    inbox_dir = vault / "_System" / "AnyContent" / "inbox"
    before = raw_snapshot(raw_dir)
    inbox_path = submit_to_inbox(inbox_dir, selected_text, label=selected_url)
    raw_path = wait_for_new_raw(raw_dir, before, timeout=timeout)
    title, source_md = build_source(vault, raw_path, read_text(raw_path), capture_path)
    out_path = vault / "10_Sources" / today() / f"{slugify(title)}.md"
    if write:
        write_text(out_path, source_md)
    print(f"inbox={inbox_path}")
    print(f"raw={raw_path}")
    print(f"source={out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Trigger AnyContent and convert raw output into a draft Source note.")
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault.")
    parser.add_argument("--capture-file", help="Capture file to read links from.")
    parser.add_argument("--text", help="Share text or URL.")
    parser.add_argument("--index", type=int, default=0, help="Which supported URL to process.")
    parser.add_argument("--timeout", type=int, default=360)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    capture_path = Path(args.capture_file).expanduser().resolve() if args.capture_file else None
    if capture_path:
        share_text = read_text(capture_path)
    elif args.text:
        share_text = args.text
    else:
        raise SystemExit("Provide --capture-file or --text.")

    process_one(vault, share_text, capture_path, args.index, args.timeout, write=not args.dry_run)


if __name__ == "__main__":
    main()
