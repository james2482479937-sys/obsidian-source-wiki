from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


VAULT = Path(r"C:\Users\24824\iCloudDrive\iCloud~md~obsidian\常用")
CANONICAL_REPO = Path(r"C:\Users\24824\Documents\Codex\2026-06-10\obsidian-codex-app-karpathy-llm-wiki")
CANONICAL_SCRIPT = CANONICAL_REPO / "obsidian-source-wiki" / "scripts" / "process_capture_links.py"
VALIDATOR = CANONICAL_REPO / "obsidian-source-wiki" / "scripts" / "validate_source_structure.py"
BACKEND_DIR = Path(r"C:\Users\24824\Documents\anycontent-obsidian-backend")
ROUTER_TMP_DIR = Path(r"C:\Users\24824\Documents\写作\outputs\obsidian-router")

URL_RE = re.compile(r"https?://[^\s\]\)）>\"']+")


def extract_processed_results(output: str) -> list[dict]:
    marker = "processed_results:"
    if marker not in output:
        return []
    payload = output.split(marker, 1)[1].strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return []


def normalize_url(url: str) -> str:
    return url.strip().rstrip("，。,.、；;：:）)]}>")


def urls_in_text(text: str) -> list[str]:
    return [normalize_url(match.group(0)) for match in URL_RE.finditer(text)]


def source_urls() -> set[str]:
    sources_dir = VAULT / "10_Sources"
    seen: set[str] = set()
    if not sources_dir.exists():
        return seen
    for path in sources_dir.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("source_url:") or stripped.startswith("- 原链接：") or stripped.startswith("source:"):
                for url in urls_in_text(stripped):
                    seen.add(normalize_url(url))
    return seen


def discover_capture_files(date: str, explicit: str) -> list[Path]:
    if explicit:
        return [Path(explicit).expanduser().resolve()]

    external = VAULT / "00_Capture" / "External"
    candidates: list[Path] = []

    date_folder = external / date
    if date_folder.exists():
        candidates.extend(sorted(path for path in date_folder.glob("*.md") if path.is_file()))

    if external.exists():
        top_level = sorted(path for path in external.glob("*.md") if path.is_file())
        candidates.extend(top_level)

    unique: list[Path] = []
    seen_paths: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved not in seen_paths:
            unique.append(resolved)
            seen_paths.add(resolved)
    return unique


def build_new_link_capture(capture_files: list[Path], date: str) -> tuple[Path | None, list[str]]:
    already_seen = source_urls()
    new_lines: list[str] = []
    new_urls: list[str] = []

    for capture_file in capture_files:
        if not capture_file.exists():
            continue
        text = capture_file.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            line_urls = urls_in_text(line)
            if not line_urls:
                continue
            unknown_urls = [url for url in line_urls if normalize_url(url) not in already_seen]
            if not unknown_urls:
                continue
            new_lines.append(line)
            new_urls.extend(unknown_urls)
            already_seen.update(unknown_urls)

    if not new_lines:
        return None, []

    ROUTER_TMP_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = ROUTER_TMP_DIR / f"{date}_new_external_links.md"
    temp_file.write_text("\n".join(new_lines).strip() + "\n", encoding="utf-8")
    return temp_file, new_urls


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AI writing project router for the canonical Obsidian Source Wiki pipeline."
    )
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--capture-file", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not CANONICAL_SCRIPT.exists():
        print(f"ERROR: canonical script not found: {CANONICAL_SCRIPT}", file=sys.stderr)
        return 2
    if not VAULT.exists():
        print(f"ERROR: vault not found: {VAULT}", file=sys.stderr)
        return 2

    capture_files = discover_capture_files(args.date, args.capture_file)
    if not capture_files:
        print("route=obsidian-source-wiki")
        print(f"vault={VAULT}")
        print(f"date={args.date}")
        print("status=no_capture_files")
        print("message=No External capture markdown files found in date folder or top-level External folder.")
        return 0

    temp_capture, new_urls = build_new_link_capture(capture_files, args.date)

    print("route=obsidian-source-wiki")
    print(f"vault={VAULT}")
    print(f"date={args.date}")
    print(f"canonical_script={CANONICAL_SCRIPT}")
    print("capture_files:")
    for path in capture_files:
        print(f"- {path}")

    if not temp_capture:
        print("status=no_new_links")
        print("message=All detected Capture links already appear in 10_Sources source_url/original links.")
        return 0

    print("new_urls:")
    for url in new_urls:
        print(f"- {url}")
    print(f"router_capture_file={temp_capture}")
    print("")

    command = [
        sys.executable,
        str(CANONICAL_SCRIPT),
        "--vault",
        str(VAULT),
        "--assume-ready",
        "--backend-dir",
        str(BACKEND_DIR),
        "--capture-file",
        str(temp_capture),
    ]
    if args.dry_run:
        command.append("--dry-run")

    result = subprocess.run(
        command,
        cwd=str(CANONICAL_REPO),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)

    if result.returncode != 0:
        return result.returncode

    if args.dry_run:
        return 0

    processed = extract_processed_results(result.stdout)
    source_paths = [item.get("source_path") for item in processed if item.get("source_path")]
    raw_paths = [item.get("raw_path") for item in processed if item.get("raw_path")]

    print("")
    print("agent_next_step=semantic_structure_required")
    if source_paths:
        print("source_paths:")
        for path in source_paths:
            print(f"- {path}")
    if raw_paths:
        print("raw_paths:")
        for path in raw_paths:
            print(f"- {path}")
    print(f"validator={VALIDATOR}")
    print(
        "completion_rule=For every source_path, rewrite semantic H2 headings and natural paragraphs, "
        "set frontmatter to source_structured/capture_source/knowledge_status/reading_status, "
        "then run the validator before reporting done."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
