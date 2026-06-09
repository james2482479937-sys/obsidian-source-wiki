# Troubleshooting

## AnyContent Creates Raw But Script Fails

Console output may fail on Windows if filenames contain emoji or Chinese characters. Check `_System/AnyContent/raw` and `10_Sources/YYYY-MM-DD` before rerunning.

## Xiaohongshu OCR Fails

Check whether the API key has balance and access to a vision model. If the first image returns insufficient balance, do not keep retrying every image.

The tested failure text was `account balance is insufficient`. In that case, mark the Source `needs_ocr` or ask the user to recharge/configure a usable OCR provider, then rerun the adapter.

If parsing fails, open the resolved Xiaohongshu page and inspect whether `window.__INITIAL_STATE__` still contains `noteDetailMap`.

## Video Download Fails

Retry with resumable download if possible. Xiaohongshu CDN can break mid-stream. Temporary media should remain under `_System/AnyContent/media` and be deleted after success.

## Obsidian Plugins Create Extra Folders

Patch plugin settings to put output under `_System`. If a plugin still creates a root folder, move only after verifying the plugin will not break, or leave it and document why.

## Source Looks Too Mechanical

The script generated only a draft. The agent must run the semantic structuring pass from `source_structuring.md`.

## Knowledge Note Is Not Linked Back

Use `scripts/create_knowledge_note.py` instead of manually creating a Knowledge file. It creates the Knowledge scaffold and updates the Source note's `knowledge_links` plus `Linked Knowledge` section.
