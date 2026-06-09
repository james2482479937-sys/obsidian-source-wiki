import argparse
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


IMAGE_URL = re.compile(r"https?://[^\s<>)]+(?:\.webp|\.jpg|\.jpeg|\.png)(?:\?[^\s<>)]+)?", re.I)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def title_from_markdown(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, flags=re.M)
    if not match:
        return fallback
    title = re.sub(r'[\\/:*?"<>|#^\[\]]+', "", match.group(1)).strip()
    return title[:80] or fallback


def platform_from_frontmatter(text: str) -> str:
    match = re.search(r"^platform:\s*([^\n]+)$", text, flags=re.M)
    return (match.group(1).strip().strip('"') if match else "unknown").title()


def extract_image_urls(text: str) -> list[str]:
    urls = []
    for match in IMAGE_URL.finditer(text):
        url = match.group(0).rstrip(".,;，。；")
        if url not in urls:
            urls.append(url)
    return urls


def extension_for_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for ext in (".webp", ".jpg", ".jpeg", ".png"):
        if ext in path:
            return ext
    return ".jpg"


def download(url: str, path: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.douyin.com/",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        path.write_bytes(response.read())


def main() -> None:
    parser = argparse.ArgumentParser(description="Download image URLs referenced by a raw Source file.")
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault.")
    parser.add_argument("--raw-file", required=True, help="Raw Markdown file containing image URLs.")
    parser.add_argument("--date", help="Date folder. Defaults to today's date from the local machine.")
    args = parser.parse_args()

    import datetime as dt

    vault = Path(args.vault).expanduser().resolve()
    raw_file = Path(args.raw_file).expanduser().resolve()
    text = read_text(raw_file)
    urls = extract_image_urls(text)
    if not urls:
        raise SystemExit("No image URLs found in raw file.")

    platform = platform_from_frontmatter(text)
    title = title_from_markdown(text, raw_file.stem)
    date = args.date or dt.date.today().isoformat()
    out_dir = vault / "_System" / "Attachments" / platform / date / title
    out_dir.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(urls, start=1):
        out_path = out_dir / f"image-{index:02d}{extension_for_url(url)}"
        download(url, out_path)
        print(f"saved={out_path}")

    print(f"count={len(urls)}")
    print(f"attachment_dir={out_dir}")


if __name__ == "__main__":
    main()
