import argparse
import datetime as dt
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


XHS_URL = re.compile(r"https?://(?:xhslink\.com|www\.xiaohongshu\.com)/[^\s，。；;]+", re.I)
ANYCONTENT_URL = re.compile(
    r"https?://(?:v\.douyin\.com|www\.douyin\.com|www\.iesdouyin\.com|"
    r"www\.tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com|"
    r"mp\.weixin\.qq\.com|www\.youtube\.com|youtube\.com|youtu\.be|m\.youtube\.com)"
    r"[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+",
    re.I,
)
SAVE_IMAGE_HINTS = ("保存图片", "留图", "下载图片", "下载原图", "保留图片")


def today() -> str:
    return dt.date.today().isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def scripts_dir() -> Path:
    return Path(__file__).resolve().parent


def backend_reachable(host: str = "127.0.0.1", port: int = 8080) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def discover_backend_dir(explicit: str | None) -> Path | None:
    candidates = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    env_path = os.environ.get("ANYCONTENT_BACKEND_DIR")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend(
        [
            Path.cwd() / "anycontent-obsidian-backend",
            Path.home() / "Documents" / "anycontent-obsidian-backend",
            Path.home() / "anycontent-obsidian-backend",
        ]
    )
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "web" / "app.py").exists():
            return resolved
    return None


def ensure_anycontent_backend(vault: Path, backend_dir_arg: str | None, startup_timeout: int) -> None:
    if backend_reachable():
        print("anycontent_backend=already_running http://127.0.0.1:8080")
        return

    backend_dir = discover_backend_dir(backend_dir_arg)
    if not backend_dir:
        raise SystemExit(
            "AnyContent backend is not running and the backend directory was not found. "
            "Clone it first, or pass --backend-dir \"<path-to-anycontent-obsidian-backend>\"."
        )

    uv_path = shutil.which("uv")
    if not uv_path:
        raise SystemExit("AnyContent backend is not running and uv was not found in PATH.")

    log_dir = vault / "_System" / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "anycontent-backend.log"
    log_file = log_path.open("a", encoding="utf-8")

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    process = subprocess.Popen(
        [uv_path, "run", "python", "web/app.py"],
        cwd=backend_dir,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=creationflags,
    )

    deadline = time.time() + startup_timeout
    while time.time() < deadline:
        if backend_reachable():
            print(f"anycontent_backend=started pid={process.pid} log={log_path}")
            return
        if process.poll() is not None:
            raise SystemExit(f"AnyContent backend exited early. Check log: {log_path}")
        time.sleep(1)

    raise SystemExit(f"Timed out starting AnyContent backend. Check log: {log_path}")


def default_capture_files(vault: Path, date: str) -> list[Path]:
    folder = vault / "00_Capture" / "External" / date
    if not folder.exists():
        return []
    return sorted(path for path in folder.glob("*.md") if path.is_file())


def extract_items(path: Path) -> list[dict]:
    text = read_text(path)
    items = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        urls = []
        urls.extend(("xhs", match.group(0).rstrip(".,;，。；")) for match in XHS_URL.finditer(line))
        urls.extend(("anycontent", match.group(0).rstrip(".,;，。；")) for match in ANYCONTENT_URL.finditer(line))
        for platform, url in urls:
            items.append(
                {
                    "platform": platform,
                    "url": url,
                    "line": line.strip() or url,
                    "line_number": line_number,
                    "capture_file": str(path),
                    "save_images": any(hint in line for hint in SAVE_IMAGE_HINTS),
                }
            )
    return items


def run(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + " ".join(command)
            + "\nSTDOUT:\n"
            + result.stdout
            + "\nSTDERR:\n"
            + result.stderr
        )
    return result.stdout


def parse_key_value_path(output: str, key: str) -> Path | None:
    match = re.search(rf"^{re.escape(key)}=(.+)$", output, flags=re.M)
    return Path(match.group(1).strip()) if match else None


def parse_json_path(output: str, key: str) -> Path | None:
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return None
    value = data.get(key)
    return Path(value) if value else None


def save_images(vault: Path, raw_path: Path, cwd: Path) -> str:
    return run(
        [
            sys.executable,
            str(cwd / "save_images_from_raw.py"),
            "--vault",
            str(vault),
            "--raw-file",
            str(raw_path),
        ],
        cwd=cwd,
    )


def process_item(vault: Path, item: dict, timeout: int, assume_ready: bool) -> dict:
    cwd = scripts_dir()
    result = {
        "platform": item["platform"],
        "url": item["url"],
        "capture_file": item["capture_file"],
        "line_number": item["line_number"],
        "save_images": item["save_images"],
    }

    if item["platform"] == "xhs":
        output = run(
            [
                sys.executable,
                str(cwd / "xhs_to_source.py"),
                "--vault",
                str(vault),
                "--url",
                item["url"],
                "--write",
            ],
            cwd=cwd,
        )
        raw_path = parse_json_path(output, "raw_path")
        source_path = parse_json_path(output, "source_path")
    else:
        command = [
            sys.executable,
            str(cwd / "anycontent_to_source.py"),
            "--vault",
            str(vault),
            "--text",
            item["line"],
            "--timeout",
            str(timeout),
        ]
        output = run(command, cwd=cwd)
        raw_path = parse_key_value_path(output, "raw")
        source_path = parse_key_value_path(output, "source")

    result["raw_path"] = str(raw_path) if raw_path else ""
    result["source_path"] = str(source_path) if source_path else ""

    if item["save_images"] and raw_path:
        image_output = save_images(vault, raw_path, cwd)
        result["image_save_output"] = image_output.strip()
    result["status"] = "draft_source_created"
    result["next_step"] = "Run semantic Source structuring before treating the note as final."
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Process Capture links through the appropriate Obsidian Source Wiki route.")
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault.")
    parser.add_argument("--capture-file", help="Specific Capture markdown file. Defaults to all External files for --date.")
    parser.add_argument("--date", default=today(), help="Capture date folder, default today.")
    parser.add_argument("--timeout", type=int, default=360, help="AnyContent wait timeout.")
    parser.add_argument("--assume-ready", action="store_true", help="Skip environment check for already configured vaults.")
    parser.add_argument("--backend-dir", help="Path to anycontent-obsidian-backend. Auto-discovered if omitted.")
    parser.add_argument("--backend-startup-timeout", type=int, default=60, help="Seconds to wait for AnyContent backend startup.")
    parser.add_argument("--no-start-backend", action="store_true", help="Do not auto-start AnyContent backend.")
    parser.add_argument("--dry-run", action="store_true", help="Only print detected routes.")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    capture_files = [Path(args.capture_file).expanduser().resolve()] if args.capture_file else default_capture_files(vault, args.date)
    if not capture_files:
        raise SystemExit(f"No capture files found for date {args.date}.")

    items = []
    for path in capture_files:
        items.extend(extract_items(path))
    if not items:
        raise SystemExit("No supported Douyin/Xiaohongshu links found.")

    print("detected_routes:")
    for index, item in enumerate(items, start=1):
        save = " save_images" if item["save_images"] else ""
        print(f"{index}. {item['platform']} line={item['line_number']}{save} {item['url']}")

    if args.dry_run:
        return

    has_anycontent_route = any(item["platform"] == "anycontent" for item in items)
    if has_anycontent_route and not args.no_start_backend:
        ensure_anycontent_backend(vault, args.backend_dir, args.backend_startup_timeout)

    if not args.assume_ready:
        env_output = run(
            [sys.executable, str(scripts_dir() / "check_environment.py"), "--vault", str(vault)],
            cwd=scripts_dir(),
        )
        if "environment_ready=true" not in env_output:
            print(env_output)
            raise SystemExit("Environment is not ready. Fix missing requirements or rerun with --assume-ready if you know it is configured.")

    results = []
    for item in items:
        results.append(process_item(vault, item, args.timeout, args.assume_ready))

    print("processed_results:")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
