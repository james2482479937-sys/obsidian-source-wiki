---
name: obsidian-source-wiki
description: Build and operate an Obsidian-based AI knowledge workflow with Capture, Sources, Knowledge, Rules, and System folders. Use when the user wants to set up an Obsidian vault, configure required plugins and API prerequisites, install or explain AnyContent/SiliconFlow/ffmpeg setup, process Douyin or Xiaohongshu video/image/text links into structured Source notes, distill Source notes into Knowledge notes, or understand this AI-assisted personal wiki workflow. During first-time setup, the agent must not stop after creating folders; it must also tell the user which plugins, backend services, API keys, and local tools are required before media import can work.
---

# Obsidian Source Wiki

Version: 0.3.1

Use this skill to help a user build or operate an Obsidian knowledge workflow where plugins import raw material, scripts bridge unsupported platforms, and the agent performs semantic structuring and knowledge distillation.

## Core Model

Treat the vault as five areas:

- `00_Capture`: daily lightweight capture.
- `10_Sources`: structured source material for future reading and traceability.
- `20_Knowledge`: distilled evergreen concepts, methods, projects, workflows, and media notes.
- `90_Rules`: rules that govern capture, source structuring, cleanup, naming, and knowledge distillation.
- `_System`: plugin output, raw transcripts, media temp files, attachments, and logs.

Read `references/folder_schema.md` before changing folder design.

## First-Time Setup Protocol

When a user asks to create this workflow for a new vault, do all of the following. Do not stop after creating folders.

1. Discover or ask for the Obsidian vault path.
2. Run `scripts/setup_vault.py --vault "<vault>" --configure-plugins` to create the folder system and copy rule files.
3. Run `scripts/check_environment.py --vault "<vault>"`.
4. Read `references/plugin_setup.md`.
5. Report a setup checklist to the user with three sections:
   - Already done: folders, rules, detected plugins/tools.
   - User must install or register: missing Obsidian plugins, AnyContent backend, SiliconFlow API key, ffmpeg, Python dependencies.
   - Blocked media features: which import routes cannot work until the missing items are complete.
6. If AnyContent or SiliconFlow API key is missing, clearly say that Douyin video/image import, Xiaohongshu video ASR, and Xiaohongshu image OCR are not ready yet.
7. After the user confirms the missing prerequisites are done, rerun `scripts/check_environment.py --vault "<vault>"` before processing links.

Minimum requirements for the full workflow:

- Obsidian desktop app with Community plugins enabled.
- AnyContent Vault Importer plugin installed and enabled.
- AnyContent backend running at `http://127.0.0.1:8080`.
- SiliconFlow account and API key configured in AnyContent plugin settings.
- `ffmpeg` available for video audio extraction.
- Python available for running the bundled scripts.
- Python package `requests` available for the Xiaohongshu adapter.

Recommended optional plugins:

- XHS Importer for manual Xiaohongshu clipping.
- Mind Elixir Mind Map for heading-to-mindmap viewing.
- QuickAdd for capture shortcuts.
- Excalidraw for sketches and diagrams.

## Operating Workflow

1. Discover the user's vault path.
2. Run `scripts/check_environment.py --vault "<vault>"` to inspect plugins, API key, Python, ffmpeg, and `_System`.
3. If setting up a new vault, run `scripts/setup_vault.py --vault "<vault>" --configure-plugins`.
4. Read `references/plugin_setup.md` before editing plugin settings.
5. Read `references/media_pipeline.md` before processing Douyin/Xiaohongshu links.
6. Use `scripts/anycontent_to_source.py` for AnyContent-supported links such as Douyin video/image posts.
7. Use `scripts/xhs_to_source.py` for Xiaohongshu video/image posts.
8. If the capture text explicitly asks to save images, use `scripts/save_images_from_raw.py` on the raw file and link the saved files from the Source note.
9. After raw import, read `references/source_structuring.md` and polish the Source note into a readable, semantically titled Source.
10. When asked to extract lasting knowledge, read `references/knowledge_distillation.md`.
11. Use `scripts/create_knowledge_note.py` to create the Knowledge note scaffold and update the Source backlink.
12. Fill the generated Knowledge note with the distilled concept, method, project, workflow, or media note.

## Fast Path for Configured Vaults

If the user says their Obsidian/AnyContent/SiliconFlow/ffmpeg environment is already configured, do not spend tokens re-explaining first-time setup.

Use:

```powershell
python scripts/process_capture_links.py --vault "<vault>" --capture-file "<capture-file>" --assume-ready
```

or for today's whole External capture folder:

```powershell
python scripts/process_capture_links.py --vault "<vault>" --date YYYY-MM-DD --assume-ready
```

This script routes:

- Douyin/TikTok/WeChat/YouTube links to AnyContent,
- Xiaohongshu links to the Xiaohongshu adapter,
- explicit image-saving requests to `save_images_from_raw.py`.

For AnyContent routes, the unified processor first checks `http://127.0.0.1:8080`. If the backend is not running, it auto-discovers `anycontent-obsidian-backend` and starts the same backend command used manually:

```powershell
uv run python web/app.py
```

If the backend repo is not in a common location, pass it explicitly:

```powershell
python scripts/process_capture_links.py --vault "<vault>" --date YYYY-MM-DD --assume-ready --backend-dir "<path-to-anycontent-obsidian-backend>"
```

Use `--no-start-backend` only when debugging and you want to manage the backend manually.

After it creates draft Source notes, run the semantic Source structuring pass.

## Important Boundaries

- Do not delete user notes or raw captures unless explicitly asked.
- Do not store API keys inside the skill. Read them from the user's existing plugin settings or environment.
- Do not put plugin temp output in the main knowledge areas. Keep it under `_System`.
- Do not treat raw transcripts or OCR dumps as final Source notes.
- Do not turn Source notes into summaries. Source notes should preserve source meaning and improve readability.
- Only Knowledge notes should distill, generalize, compare, and link ideas.
- By default, do not save image attachments. Save images only when the capture text near the link says `保存图片`, `留图`, `下载图片`, `下载原图`, or an equivalent instruction.

## Resource Map

- Folder design: `references/folder_schema.md`
- Capture rules: `references/capture_rules.md`
- User prompts: `references/onboarding_prompts.md`
- Plugin setup: `references/plugin_setup.md`
- Media processing: `references/media_pipeline.md`
- Source polishing: `references/source_structuring.md`
- Knowledge notes: `references/knowledge_distillation.md`
- Failure handling: `references/troubleshooting.md`
- Reusable scripts: `scripts/`
- Unified Capture processor: `scripts/process_capture_links.py`
- Knowledge linking helper: `scripts/create_knowledge_note.py`
- Rule templates to copy into vaults: `assets/rules/`
