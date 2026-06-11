#!/usr/bin/env python3
"""Generate a local rich-text copy preview page from an article text file."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


P_STYLE = "margin:0 0 22px;line-height:2.05;font-size:17px;color:#20242a;"
H1_STYLE = "margin:0 0 24px;line-height:1.32;font-size:30px;font-weight:800;color:#1f2329;"
H2_STYLE = "margin:34px 0 18px;line-height:1.45;font-size:23px;font-weight:800;color:#1f2329;"
BQ_STYLE = "margin:8px 0 28px;padding:20px 24px;border-left:4px solid #1bbf68;background:#f3fbf6;color:#404a45;line-height:2.05;font-size:17px;"
HR_STYLE = "border:none;border-top:1px solid #dfe4ea;margin:34px 0;"
UL_STYLE = "margin:0 0 24px 22px;padding:0;line-height:1.95;font-size:17px;color:#20242a;"
LI_STYLE = "margin:0 0 12px;padding-left:4px;"


def inline_md(value: str) -> str:
    escaped = html.escape(value)
    return re.sub(
        r"\*\*(.+?)\*\*",
        r'<strong style="font-weight:800;color:#111827;">\1</strong>',
        escaped,
    )


def render_markdown(markdown: str, include_title: bool = True) -> str:
    result: list[str] = []
    para: list[str] = []
    quote: list[str] = []
    items: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            content = "<br>".join(inline_md(x.strip()) for x in para if x.strip())
            if content:
                result.append(f'<p style="{P_STYLE}">{content}</p>')
            para = []

    def flush_quote() -> None:
        nonlocal quote
        if quote:
            content = "<br>".join(inline_md(x.strip()) for x in quote if x.strip())
            if content:
                result.append(f'<blockquote style="{BQ_STYLE}">{content}</blockquote>')
            quote = []

    def flush_items() -> None:
        nonlocal items
        if items:
            li = "".join(f'<li style="{LI_STYLE}">{inline_md(x)}</li>' for x in items)
            result.append(f'<ul style="{UL_STYLE}">{li}</ul>')
            items = []

    for raw in markdown.splitlines():
        stripped = raw.strip()
        if not stripped:
            flush_quote()
            flush_items()
            flush_para()
            continue
        if stripped == "---":
            flush_quote()
            flush_items()
            flush_para()
            result.append(f'<hr style="{HR_STYLE}">')
            continue
        if stripped.startswith("# "):
            flush_quote()
            flush_items()
            flush_para()
            if include_title:
                result.append(f'<h1 style="{H1_STYLE}">{inline_md(stripped[2:].strip())}</h1>')
            continue
        if stripped.startswith("## "):
            flush_quote()
            flush_items()
            flush_para()
            result.append(f'<h2 style="{H2_STYLE}">{inline_md(stripped[3:].strip())}</h2>')
            continue
        if stripped.startswith(">"):
            flush_items()
            flush_para()
            quote.append(stripped.lstrip(">").strip())
            continue
        if stripped.startswith("- "):
            flush_quote()
            flush_para()
            items.append(stripped[2:].strip())
            continue
        flush_quote()
        flush_items()
        para.append(stripped)

    flush_quote()
    flush_items()
    flush_para()
    return "\n".join(result)


def article_title(markdown: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return "Article Preview"


def body_markdown(markdown: str) -> str:
    lines = [line for line in markdown.splitlines() if not line.strip().startswith("# ")]
    return "\n".join(lines).strip() + "\n"


def build_html(markdown: str) -> str:
    title = article_title(markdown)
    full_md = markdown.strip() + "\n"
    body_md = body_markdown(full_md)
    body_html = render_markdown(body_md, include_title=False)
    full_html = render_markdown(full_md, include_title=True)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  :root {{ color-scheme: light; --bg:#f6f7f9; --ink:#1f2329; --muted:#6b7280; --line:#dde3ea; --green:#16a34a; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",Arial,sans-serif; }}
  .topbar {{ position:sticky; top:0; z-index:20; display:flex; align-items:center; justify-content:space-between; gap:16px; padding:14px 22px; background:rgba(255,255,255,.96); border-bottom:1px solid var(--line); backdrop-filter:saturate(180%) blur(10px); }}
  .brand {{ min-width:0; }}
  .brand-title {{ margin:0; font-size:16px; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
  .brand-sub {{ margin-top:4px; font-size:13px; color:var(--muted); }}
  .actions {{ display:flex; align-items:center; gap:10px; flex-shrink:0; }}
  button {{ border:1px solid var(--line); border-radius:8px; padding:10px 16px; font-size:15px; font-weight:700; background:#fff; color:#111827; cursor:pointer; min-width:96px; }}
  button.primary {{ background:#111827; border-color:#111827; color:#fff; }}
  #copymsg {{ min-width:150px; font-size:14px; color:var(--green); font-weight:700; }}
  main {{ width:min(920px, calc(100vw - 40px)); margin:28px auto 70px; }}
  .notice {{ margin:0 0 26px; padding:14px 18px; border-radius:8px; background:#fff7ed; color:#9a3412; font-size:14px; line-height:1.7; }}
  .article {{ background:#fff; padding:42px 50px 54px; border:1px solid var(--line); border-radius:10px; }}
  .manual-title {{ margin:30px 0 10px; font-size:16px; font-weight:800; color:#111827; }}
  .manual-tip {{ margin:0 0 12px; color:var(--muted); font-size:14px; line-height:1.7; }}
  .manual-box {{ background:#fff; border:1px dashed #aeb7c4; border-radius:8px; padding:26px 34px; min-height:180px; outline:none; }}
  #copy-buffer {{ position:fixed; left:0; top:0; width:860px; max-height:70vh; overflow:hidden; opacity:.01; z-index:9999; pointer-events:none; background:#fff; color:#000; }}
  @media (max-width:700px) {{ .topbar {{ align-items:flex-start; flex-direction:column; }} .actions {{ width:100%; flex-wrap:wrap; }} button {{ flex:1; min-width:120px; }} main {{ width:calc(100vw - 24px); margin-top:16px; }} .article {{ padding:28px 22px 36px; }} }}
</style>
</head>
<body>
<header class="topbar">
  <div class="brand">
    <div class="brand-title">{html.escape(title)}</div>
    <div class="brand-sub">&#x672c;&#x5730;&#x53ef;&#x590d;&#x5236;&#x9884;&#x89c8;&#x9875; / Rich text copy</div>
  </div>
  <div class="actions">
    <button class="primary" type="button" onclick="copyArticle('body')">&#x590d;&#x5236;&#x6b63;&#x6587;</button>
    <button type="button" onclick="copyArticle('full')">&#x590d;&#x5236;&#x5168;&#x6587;</button>
    <span id="copymsg" aria-live="polite"></span>
  </div>
</header>
<main>
  <p class="notice">&#x590d;&#x5236;&#x6b63;&#x6587;&#xFF1A;&#x4E0D;&#x542B;&#x5927;&#x6807;&#x9898;&#xFF0C;&#x9002;&#x5408;&#x7C98;&#x8D34;&#x5230;&#x201C;&#x4EBA;&#x4EBA;&#x90FD;&#x662F;&#x4EA7;&#x54C1;&#x7ECF;&#x7406;&#x201D;&#x7684;&#x6B63;&#x6587;&#x533A;&#x3002;&#x590d;&#x5236;&#x5168;&#x6587;&#xFF1A;&#x5305;&#x542B;&#x5927;&#x6807;&#x9898;&#xFF0C;&#x5907;&#x7528;&#x3002;&#x8FD9;&#x4E24;&#x4E2A;&#x6309;&#x94AE;&#x590D;&#x5236;&#x7684;&#x662F;&#x5DF2;&#x6E32;&#x67D3;&#x7684;&#x5BCC;&#x6587;&#x672C;&#xFF0C;&#x4E0D;&#x662F; Markdown &#x6E90;&#x7801;&#x3002;</p>
  <article class="article" id="article-preview">
{full_html}
  </article>
  <div class="manual-title">&#x5907;&#x7528;&#x624B;&#x52A8;&#x590D;&#x5236;&#x533A;</div>
  <p class="manual-tip">&#x5982;&#x679C;&#x6D4F;&#x89C8;&#x5668;&#x62E6;&#x622A;&#x6309;&#x94AE;&#x590D;&#x5236;&#xFF0C;&#x70B9;&#x4E0B;&#x9762;&#x8FD9;&#x4E2A;&#x6846;&#x91CC;&#x9762;&#xFF0C;&#x518D;&#x6309; Ctrl+A&#x3001;Ctrl+C&#x3002;&#x8FD9;&#x91CC;&#x540C;&#x6837;&#x662F;&#x5DF2;&#x6E32;&#x67D3;&#x7684;&#x6B63;&#x6587;&#x3002;</p>
  <div class="manual-box" id="manual-copy" contenteditable="true">
{body_html}
  </div>
</main>
<div id="copy-buffer" contenteditable="true"></div>
<span id="msg-body" hidden>&#x5DF2;&#x590D;&#x5236;&#x6B63;&#x6587;</span>
<span id="msg-full" hidden>&#x5DF2;&#x590D;&#x5236;&#x5168;&#x6587;</span>
<span id="msg-failed" hidden>&#x590D;&#x5236;&#x5931;&#x8D25;&#xFF0C;&#x8BF7;&#x7528;&#x4E0B;&#x65B9;&#x5907;&#x7528;&#x590D;&#x5236;&#x533A;</span>
<script>
const BODY_HTML = {json.dumps(body_html, ensure_ascii=False)};
const FULL_HTML = {json.dumps(full_html, ensure_ascii=False)};
const BODY_TEXT = {json.dumps(body_md, ensure_ascii=False)};
const FULL_TEXT = {json.dumps(full_md, ensure_ascii=False)};

function showMessage(id) {{
  const box = document.getElementById('copymsg');
  box.textContent = document.getElementById(id).textContent;
  window.clearTimeout(window.__copyMsgTimer);
  window.__copyMsgTimer = window.setTimeout(() => {{ box.textContent = ''; }}, 2600);
}}

function selectAndCopy(node) {{
  node.focus();
  const range = document.createRange();
  range.selectNodeContents(node);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
  let ok = false;
  try {{ ok = document.execCommand('copy'); }} catch (err) {{ ok = false; }}
  sel.removeAllRanges();
  return ok;
}}

function copyByEvent(rich, plain) {{
  let wrote = false;
  const marker = document.createElement('span');
  marker.textContent = plain.slice(0, 1) || ' ';
  marker.setAttribute('contenteditable', 'true');
  marker.style.position = 'fixed';
  marker.style.left = '12px';
  marker.style.top = '12px';
  marker.style.opacity = '0.01';
  marker.style.zIndex = '99999';
  marker.style.background = '#fff';
  document.body.appendChild(marker);

  function onCopy(event) {{
    if (event.clipboardData) {{
      event.clipboardData.setData('text/html', rich);
      event.clipboardData.setData('text/plain', plain);
      event.preventDefault();
      wrote = true;
    }}
  }}

  document.addEventListener('copy', onCopy, {{ once: true }});
  marker.focus();
  const range = document.createRange();
  range.selectNodeContents(marker);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
  let copied = false;
  try {{ copied = document.execCommand('copy'); }} catch (err) {{ copied = false; }}
  sel.removeAllRanges();
  marker.remove();
  document.removeEventListener('copy', onCopy);
  return copied && wrote;
}}

async function copyArticle(kind) {{
  const rich = kind === 'full' ? FULL_HTML : BODY_HTML;
  const plain = kind === 'full' ? FULL_TEXT : BODY_TEXT;
  const done = kind === 'full' ? 'msg-full' : 'msg-body';
  const buffer = document.getElementById('copy-buffer');
  buffer.innerHTML = rich;
  try {{
    if (navigator.clipboard && window.ClipboardItem) {{
      await navigator.clipboard.write([
        new ClipboardItem({{
          'text/html': new Blob([rich], {{ type: 'text/html' }}),
          'text/plain': new Blob([plain], {{ type: 'text/plain' }})
        }})
      ]);
      showMessage(done);
      return;
    }}
  }} catch (err) {{}}
  if (copyByEvent(rich, plain)) {{
    showMessage(done);
    return;
  }}
  const fallbackNode = kind === 'full'
    ? document.getElementById('article-preview')
    : document.getElementById('manual-copy');
  if (selectAndCopy(fallbackNode)) {{
    showMessage(done);
    return;
  }}
  try {{
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      await navigator.clipboard.writeText(plain);
      showMessage(done);
      return;
    }}
  }} catch (err) {{}}
  showMessage('msg-failed');
}}
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Article .txt or .md file")
    parser.add_argument("--out-dir", default="outputs", help="Output directory")
    args = parser.parse_args()

    source = Path(args.source)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    markdown = source.read_text(encoding="utf-8-sig")
    artifact = build_html(markdown)
    for name in ("article_artifact_preview.html", "article_visual_paste.html"):
        (out_dir / name).write_text(artifact, encoding="utf-8")

    print(out_dir / "article_artifact_preview.html")


if __name__ == "__main__":
    main()
