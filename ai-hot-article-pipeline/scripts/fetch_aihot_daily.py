from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen


API_URL = "https://aihot.virxact.com/api/public/daily"


def fetch_daily() -> dict:
    request = Request(
        API_URL,
        headers={
            "User-Agent": "Codex-AIHot-Article-Pipeline/1.0",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=30) as response:
        raw = response.read()
    return json.loads(raw.decode("utf-8"))


def normalize_date(payload: dict) -> str:
    value = payload.get("date")
    if isinstance(value, str) and value.strip():
        return value[:10]
    return datetime.now().strftime("%Y-%m-%d")


def iter_sections(payload: dict):
    for section in payload.get("sections") or []:
        label = section.get("label") or "未分类"
        items = section.get("items") or []
        yield label, items


def build_daily_markdown(payload: dict) -> str:
    date = normalize_date(payload)
    generated_at = payload.get("generatedAt") or ""
    lines: list[str] = [
        f"# AI HOT 日报 - {date}",
        "",
        f"数据来源：AI HOT 主日报接口 `{API_URL}`。",
    ]
    if generated_at:
        lines.append(f"生成时间：`{generated_at}`。")
    lines.append("")

    for label, items in iter_sections(payload):
        lines.extend([f"## {label}", ""])
        if not items:
            lines.extend(["- 今日暂无条目。", ""])
            continue
        for item in items:
            title = item.get("title") or "未命名条目"
            summary = item.get("summary") or ""
            source_url = item.get("sourceUrl") or ""
            source_name = item.get("sourceName") or "来源"
            link = f"[{source_name}]({source_url})" if source_url else source_name
            lines.append(f"- **{title}**：{summary} [原文]({source_url})" if source_url else f"- **{title}**：{summary}")
            if source_url and source_name:
                lines.append(f"  - 来源：{link}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_candidates_markdown(payload: dict) -> str:
    date = normalize_date(payload)
    lines: list[str] = [
        f"# AI HOT 文章选题候选池 - {date}",
        "",
        "选题时优先看：话题性、争议性、与 Agent/AI 工具/AI 产品/普通人使用 AI 的相关度、能否写成长文。",
        "",
    ]

    index = 1
    for label, items in iter_sections(payload):
        lines.extend([f"## {label}", ""])
        for item in items:
            title = item.get("title") or "未命名条目"
            summary = item.get("summary") or ""
            source_url = item.get("sourceUrl") or ""
            source_name = item.get("sourceName") or "来源"
            lines.extend(
                [
                    f"### {index}. {title}",
                    "",
                    f"- 分类：{label}",
                    f"- 摘要：{summary}",
                    f"- 来源：{source_name}",
                    f"- 链接：{source_url}",
                    "- 可写角度：",
                    "- 适合人群：",
                    "- 争议/冲突：",
                    "",
                ]
            )
            index += 1
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="outputs/aihot")
    parser.add_argument("--legacy-report", default="")
    args = parser.parse_args()

    payload = fetch_daily()
    date = normalize_date(payload)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_path = out_dir / f"{date}_aihot_raw.json"
    daily_path = out_dir / f"{date}_aihot_daily.md"
    candidates_path = out_dir / f"{date}_aihot_candidates.md"

    raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    daily = build_daily_markdown(payload)
    candidates = build_candidates_markdown(payload)
    daily_path.write_text(daily, encoding="utf-8")
    candidates_path.write_text(candidates, encoding="utf-8")

    if args.legacy_report:
        legacy_path = Path(args.legacy_report)
        legacy_path.parent.mkdir(parents=True, exist_ok=True)
        legacy_path.write_text(daily, encoding="utf-8")

    print(f"date={date}")
    print(f"daily={daily_path.resolve()}")
    print(f"candidates={candidates_path.resolve()}")
    print(f"raw={raw_path.resolve()}")
    if args.legacy_report:
        print(f"legacy_report={Path(args.legacy_report).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
