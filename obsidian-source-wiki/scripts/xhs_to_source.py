import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

import requests


CAPTURE_NAME = "\u89c6\u9891\u94fe\u63a5.md"
ANYCONTENT_SETTINGS = ".obsidian/plugins/anycontent-vault-importer/data.json"
ASR_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"
CHAT_URL = "https://api.siliconflow.cn/v1/chat/completions"
ASR_MODEL = "FunAudioLLM/SenseVoiceSmall"
OCR_MODELS = [
    "Qwen/Qwen3-VL-8B-Instruct",
    "Qwen/Qwen3-VL-30B-A3B-Instruct",
    "Qwen/Qwen3-Omni-30B-A3B-Instruct",
]

OCR_PROMPT = """请提取图片里的文字，并尽量保留原图的信息层级。

要求：
1. 只输出图片文字本身，不要解释图片。
2. 如果原图有标题、列表、步骤，请用 Markdown 保留结构。
3. 不要润色、改写或总结原文。
4. 如果图片没有可识别文字，输出（无文字）。"""

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)


def today() -> str:
    return dt.date.today().isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_api_key(vault: Path) -> str:
    settings_path = vault / ANYCONTENT_SETTINGS
    if not settings_path.exists():
        raise SystemExit(f"Missing AnyContent settings: {settings_path}")
    data = json.loads(read_text(settings_path))
    api_key = (data.get("apiKey") or "").strip()
    if not api_key:
        raise SystemExit("AnyContent apiKey is empty.")
    return api_key


def default_capture_file(vault: Path) -> Path:
    return vault / "00_Capture" / "External" / today() / CAPTURE_NAME


def extract_xhs_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://[^\s\u3000]+", text)
    return [url.rstrip(".,;，。；") for url in urls if "xhslink.com" in url or "xiaohongshu.com" in url]


def fetch_html(url: str) -> tuple[str, str]:
    response = requests.get(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.7",
            "Referer": "https://www.xiaohongshu.com/",
        },
        allow_redirects=True,
        timeout=30,
    )
    response.raise_for_status()
    return response.text, response.url


def parse_initial_state(html: str) -> dict:
    match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(.*?)</script>", html, flags=re.S)
    if not match:
        raise ValueError("Cannot find Xiaohongshu initial state.")
    raw = match.group(1).strip().replace("undefined", "null")
    return json.loads(raw)


def pick_video_url(note: dict) -> str | None:
    stream = (((note.get("video") or {}).get("media") or {}).get("stream") or {})
    for codec in ("h264", "h265", "h266", "av1"):
        for item in stream.get(codec) or []:
            url = item.get("masterUrl") or item.get("master_url")
            if url:
                return url
            for backup in item.get("backupUrls") or item.get("backup_urls") or []:
                if backup:
                    return backup
    return None


def parse_note(html: str, final_url: str) -> dict:
    state = parse_initial_state(html)
    detail_map = (((state or {}).get("note") or {}).get("noteDetailMap") or {})
    if not detail_map:
        raise ValueError("Cannot find noteDetailMap.")
    note_id = next(iter(detail_map.keys()))
    note = ((detail_map[note_id] or {}).get("note") or {})
    user = note.get("user") or {}
    return {
        "note_id": note_id,
        "title": note.get("title") or "Untitled Xiaohongshu Note",
        "author": user.get("nickname") or "",
        "desc": note.get("desc") or "",
        "type": note.get("type") or "",
        "final_url": final_url,
        "video_url": pick_video_url(note),
        "image_urls": [
            (item.get("urlDefault") or item.get("url") or "").replace("http://", "https://", 1)
            for item in (note.get("imageList") or [])
            if item.get("urlDefault") or item.get("url")
        ],
    }


def safe_name(text: str, max_len: int = 80) -> str:
    text = re.sub(r'[\\/:*?"<>|]+', "-", text)
    text = re.sub(r"\s+", "-", text).strip("- .")
    return (text[:max_len].strip("- .") or "xiaohongshu-video")


def content_range_total(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"/(\d+)$", value)
    return int(match.group(1)) if match else None


def download_file(url: str, output: Path, retries: int = 5) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    host = urlparse(url).netloc
    total_size = None
    last_error = None

    for attempt in range(retries):
        downloaded = output.stat().st_size if output.exists() else 0
        headers = {
            "User-Agent": UA,
            "Referer": "https://www.xiaohongshu.com/",
            "Host": host,
        }
        if downloaded:
            headers["Range"] = f"bytes={downloaded}-"

        try:
            with requests.get(url, headers=headers, stream=True, timeout=120) as response:
                if downloaded and response.status_code == 200:
                    output.unlink(missing_ok=True)
                    downloaded = 0
                response.raise_for_status()

                if response.status_code == 206:
                    total_size = content_range_total(response.headers.get("Content-Range")) or total_size
                    mode = "ab"
                else:
                    content_length = response.headers.get("Content-Length")
                    total_size = int(content_length) if content_length and content_length.isdigit() else total_size
                    mode = "wb"

                with output.open(mode) as file:
                    for chunk in response.iter_content(chunk_size=256 * 1024):
                        if chunk:
                            file.write(chunk)

            if output.exists() and (total_size is None or output.stat().st_size >= total_size):
                return
        except requests.RequestException as error:
            last_error = error

        time.sleep(1 + attempt)

    raise RuntimeError(f"Video download failed after {retries} attempts: {last_error}")


def extract_audio(video_path: Path, audio_path: Path) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-acodec",
        "libmp3lame",
        "-q:a",
        "2",
        str(audio_path),
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def transcribe(audio_path: Path, api_key: str) -> str:
    with audio_path.open("rb") as file:
        files = {
            "file": (audio_path.name, file, "audio/mpeg"),
            "model": (None, ASR_MODEL),
        }
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(ASR_URL, headers=headers, files=files, timeout=240)
    response.raise_for_status()
    data = response.json()
    return (data.get("text") or "").strip()


def ocr_image(image_url: str, api_key: str) -> str:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    last_error = ""
    for model in OCR_MODELS:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": OCR_PROMPT},
                    ],
                }
            ],
            "temperature": 0,
            "max_tokens": 4096,
        }
        response = requests.post(CHAT_URL, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        last_error = f"{model}: {response.status_code} {response.text[:300]}"
        if response.status_code in {401, 403}:
            break
    return f"(OCR failed: {last_error})"


def split_sentences(text: str, max_chars: int = 260) -> list[str]:
    text = re.sub(r"\s+", "", text).strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[。！？!?])", text)
    paragraphs: list[str] = []
    current = ""
    for sentence in sentences:
        if not sentence:
            continue
        if current and len(current) + len(sentence) > max_chars:
            paragraphs.append(current)
            current = sentence
        else:
            current += sentence
    if current:
        paragraphs.append(current)
    return paragraphs


def build_raw(note: dict, transcript: str) -> str:
    created = today()
    saved_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return "\n".join(
        [
            "---",
            f'title: "{note["title"].replace(chr(34), chr(39))}"',
            f"created: {created}",
            "platform: xiaohongshu",
            "source_type: video",
            f'author: "{note["author"].replace(chr(34), chr(39))}"',
            f"source_url: {note['final_url']}",
            f"saved_at: {saved_at}",
            "status: raw_transcript",
            "tags:",
            "  - source/video",
            "  - platform/xiaohongshu",
            "---",
            "",
            f"# {note['title']}",
            "",
            "## Note Description",
            "",
            note["desc"].strip() or "(no description)",
            "",
            "## Raw Transcript",
            "",
            transcript or "(empty transcript)",
            "",
        ]
    )


def build_source(note: dict, raw_rel: str, transcript: str) -> str:
    created = today()
    saved_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    paragraphs = split_sentences(transcript)
    body = "\n\n".join(paragraphs) if paragraphs else "(empty transcript)"
    return "\n".join(
        [
            "---",
            f'title: "{note["title"].replace(chr(34), chr(39))}"',
            f"created: {created}",
            "source_type: video",
            "platform: xiaohongshu",
            f'author: "{note["author"].replace(chr(34), chr(39))}"',
            f"source_url: {note['final_url']}",
            f"raw_file: \"[[{raw_rel}]]\"",
            f"saved_at: {saved_at}",
            "status: source_draft",
            "tags:",
            "  - source/video",
            "  - platform/xiaohongshu",
            "knowledge_links: []",
            "---",
            "",
            f"# {note['title']}",
            "",
            "> 本文件由小红书视频转录生成。当前版本只完成基础分段，后续需要按 `90_Rules/70_Source_Article_Structuring` 做语义小标题和自然段精修。",
            "",
            "## Source Info",
            "",
            f"- 平台：小红书",
            f"- 作者：{note['author'] or '未知'}",
            f"- 原链接：{note['final_url']}",
            f"- 原始转录：[[{raw_rel}]]",
            "",
            "## 作者原始描述",
            "",
            note["desc"].strip() or "（无描述）",
            "",
            "## 视频转录",
            "",
            "### 待语义整理片段",
            "",
            body,
            "",
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


def build_image_raw(note: dict, ocr_items: list[tuple[str, str]]) -> str:
    created = today()
    saved_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = [
        "---",
        f'title: "{note["title"].replace(chr(34), chr(39))}"',
        f"created: {created}",
        "platform: xiaohongshu",
        "source_type: image_post",
        f'author: "{note["author"].replace(chr(34), chr(39))}"',
        f"source_url: {note['final_url']}",
        f"saved_at: {saved_at}",
        f"image_count: {len(note['image_urls'])}",
        "status: raw_ocr",
        "tags:",
        "  - source/image_post",
        "  - platform/xiaohongshu",
        "---",
        "",
        f"# {note['title']}",
        "",
        "## Note Description",
        "",
        note["desc"].strip() or "(no description)",
        "",
        "## Image OCR",
        "",
    ]
    for index, (url, text) in enumerate(ocr_items, start=1):
        parts.extend([f"### 图 {index}", "", text.strip() or "（无文字）", "", f"Source image: {url}", ""])
    return "\n".join(parts)


def build_image_source(note: dict, raw_rel: str, ocr_items: list[tuple[str, str]]) -> str:
    created = today()
    saved_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = [
        "---",
        f'title: "{note["title"].replace(chr(34), chr(39))}"',
        f"created: {created}",
        "source_type: image_post",
        "platform: xiaohongshu",
        f'author: "{note["author"].replace(chr(34), chr(39))}"',
        f"source_url: {note['final_url']}",
        f"raw_file: \"[[{raw_rel}]]\"",
        f"saved_at: {saved_at}",
        "status: source_draft",
        "tags:",
        "  - source/image_post",
        "  - platform/xiaohongshu",
        "knowledge_links: []",
        "---",
        "",
        f"# {note['title']}",
        "",
        "> 本文件由小红书图文 OCR 生成。当前版本保留图文原始信息，后续需要按 `90_Rules/70_Source_Article_Structuring` 做语义小标题和自然段精修。",
        "",
        "## Source Info",
        "",
        "- 平台：小红书",
        f"- 作者：{note['author'] or '未知'}",
        f"- 原链接：{note['final_url']}",
        f"- 原始 OCR：[[{raw_rel}]]",
        f"- 图片数量：{len(note['image_urls'])}",
        "",
        "## 作者原始描述",
        "",
        note["desc"].strip() or "（无描述）",
        "",
        "## 图片 OCR",
        "",
    ]
    for index, (_url, text) in enumerate(ocr_items, start=1):
        parts.extend([f"### 图 {index}", "", text.strip() or "（无文字）", ""])
    parts.extend(
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
    return "\n".join(parts)


def process_url(vault: Path, url: str, write: bool, keep_temp: bool) -> dict:
    api_key = load_api_key(vault)
    html, final_url = fetch_html(url)
    note = parse_note(html, final_url)
    if not note["video_url"]:
        if not note["image_urls"]:
            raise SystemExit(f"This Xiaohongshu note exposes no video or images: {note['title']}")
        ocr_items = []
        ocr_blocked = False
        for image_url in note["image_urls"]:
            if ocr_blocked:
                ocr_items.append((image_url, "(OCR skipped: previous image returned insufficient account balance.)"))
                continue
            ocr_text = ocr_image(image_url, api_key)
            if "account balance is insufficient" in ocr_text:
                ocr_blocked = True
            ocr_items.append((image_url, ocr_text))
        date_dir = today()
        file_base = safe_name(note["title"])
        raw_dir = vault / "_System" / "AnyContent" / "raw" / date_dir
        source_dir = vault / "10_Sources" / date_dir
        raw_path = raw_dir / f"{file_base}-xhs-image-raw.md"
        source_path = source_dir / f"{file_base}.md"
        raw_rel = raw_path.relative_to(vault).as_posix()
        if write:
            raw_dir.mkdir(parents=True, exist_ok=True)
            source_dir.mkdir(parents=True, exist_ok=True)
            raw_path.write_text(build_image_raw(note, ocr_items), encoding="utf-8")
            source_path.write_text(build_image_source(note, raw_rel, ocr_items), encoding="utf-8")
        return {
            "title": note["title"],
            "author": note["author"],
            "final_url": note["final_url"],
            "type": "image_post",
            "image_count": len(note["image_urls"]),
            "ocr_count": len(ocr_items),
            "raw_path": str(raw_path),
            "source_path": str(source_path),
            "written": write,
        }

    temp_root = vault / "_System" / "AnyContent" / "media" / "xhs-temp"
    temp_root.mkdir(parents=True, exist_ok=True)
    work_dir = Path(tempfile.mkdtemp(prefix=f"{note['note_id']}-", dir=temp_root))
    try:
        video_path = work_dir / "video.mp4"
        audio_path = work_dir / "audio.mp3"
        download_file(note["video_url"], video_path)
        extract_audio(video_path, audio_path)
        transcript = transcribe(audio_path, api_key)

        date_dir = today()
        file_base = safe_name(note["title"])
        raw_dir = vault / "_System" / "AnyContent" / "raw" / date_dir
        source_dir = vault / "10_Sources" / date_dir
        raw_path = raw_dir / f"{file_base}-xhs-raw.md"
        source_path = source_dir / f"{file_base}.md"
        raw_rel = raw_path.relative_to(vault).as_posix()

        if write:
            raw_dir.mkdir(parents=True, exist_ok=True)
            source_dir.mkdir(parents=True, exist_ok=True)
            raw_path.write_text(build_raw(note, transcript), encoding="utf-8")
            source_path.write_text(build_source(note, raw_rel, transcript), encoding="utf-8")

        return {
            "title": note["title"],
            "author": note["author"],
            "final_url": note["final_url"],
            "transcript_length": len(transcript),
            "raw_path": str(raw_path),
            "source_path": str(source_path),
            "written": write,
        }
    finally:
        if not keep_temp:
            shutil.rmtree(work_dir, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault.")
    parser.add_argument("--capture-file")
    parser.add_argument("--url")
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--keep-temp", action="store_true")
    args = parser.parse_args()

    vault = Path(args.vault)
    if args.url:
        url = args.url
    else:
        capture_file = Path(args.capture_file) if args.capture_file else default_capture_file(vault)
        urls = extract_xhs_urls(read_text(capture_file))
        if not urls:
            raise SystemExit(f"No Xiaohongshu links found in {capture_file}")
        if args.index < 0 or args.index >= len(urls):
            raise SystemExit(f"Index out of range. Found {len(urls)} Xiaohongshu links.")
        url = urls[args.index]

    result = process_url(vault, url, args.write, args.keep_temp)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
