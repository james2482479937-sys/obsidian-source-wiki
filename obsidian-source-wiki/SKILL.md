---
name: obsidian-source-wiki
description: Build and operate an Obsidian-based AI knowledge workflow with Capture, Sources, Knowledge, Rules, and System folders. Use when the user wants to set up an Obsidian vault, configure required plugins and API prerequisites, install or explain AnyContent/SiliconFlow/ffmpeg setup, process Douyin or Xiaohongshu video/image/text links into structured Source notes, distill Source notes into Knowledge notes, or understand this AI-assisted personal wiki workflow. During first-time setup, the agent must not stop after creating folders; it must also tell the user which plugins, backend services, API keys, and local tools are required before media import can work.
---

# Obsidian Source Wiki

Version: 0.3.2

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

When a user asks to set up this workflow for a new vault, follow this sequence. Do not stop after creating folders.

### Step 1 — Collect two answers from the user

Ask only these two questions (do not ask anything else):

1. "你的 Obsidian vault 路径是什么？"（如果能从系统推断就直接说出来让用户确认）
2. "你的 SiliconFlow API key 是什么？（在 https://siliconflow.cn 免费注册获取）"

### Step 2 — Run the onboarding script

```powershell
python obsidian-source-wiki/scripts/onboarding.py --vault "<vault>" --api-key "<sk-xxx>"
```

This single script handles everything automatically:
- installs uv, ffmpeg, Python requests
- clones anycontent-obsidian-backend
- creates vault folder structure and rule files
- writes the API key into AnyContent plugin settings
- runs check_environment and reports status

### Step 3 — Guide the user through Obsidian installation (if needed)

If `check_environment.py` reports `plugins_dir_exists=false`, Obsidian is not installed or the vault has never been opened. Guide the user through the following steps — you can run the download command or open the URL for them:

**Install Obsidian:**

- Windows: `winget install Obsidian.Obsidian` (or download from https://obsidian.md/download)
- Mac: `brew install --cask obsidian` (or download from https://obsidian.md/download)

**Open the vault for the first time:**

1. Launch Obsidian
2. Click "Open folder as vault"
3. Select the vault path that `onboarding.py` created

**Enable Community plugins:**

1. In Obsidian: Settings (gear icon) → Community plugins
2. Click "Turn on community plugins"

### Step 4 — Guide the user through AnyContent Vault Importer installation (if needed)

If `check_environment.py` reports `plugin:anycontent-vault-importer=missing`, guide the user:

1. In Obsidian: Settings → Community plugins → Browse
2. Search: `AnyContent Vault Importer`
3. Click Install → Enable
4. Go to the plugin settings and enter the SiliconFlow API key

After the user confirms the plugin is installed, re-run `onboarding.py` with `--api-key` so the script writes the key into the plugin's config file automatically:

```powershell
python obsidian-source-wiki/scripts/onboarding.py --vault "<vault>" --api-key "<sk-xxx>"
```

### Step 5 — Verify

After the user confirms the manual steps are done, run:

```powershell
python obsidian-source-wiki/scripts/check_environment.py --vault "<vault>"
```

Do not proceed to media processing until the output shows `environment_ready=true`.

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
9. After raw import, read `references/source_structuring.md` and polish every returned `source_path` into a readable Source with semantic topic headings.
10. Set the polished Source frontmatter to `status: source_structured`.
11. Run `scripts/validate_source_structure.py --source "<source_path>"`.
12. If validation fails, keep editing the Source. Do not report the import as complete while validation fails.
13. When asked to extract lasting knowledge, read `references/knowledge_distillation.md`.
14. Use `scripts/create_knowledge_note.py` to create the Knowledge note scaffold and update the Source backlink.
15. Fill the generated Knowledge note with the distilled concept, method, project, workflow, or media note.

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

The unified processor only creates draft Source notes. A draft is not done.

For every returned `source_path`, the agent must immediately:

1. Read the generated Source and, when needed, the linked raw file.
2. Replace mechanical sections such as `视频转录`, `图片 OCR`, `Transcript`, or `内容` with semantic H2 headings that describe the real topic blocks.
3. Split each topic block into readable natural paragraphs.
4. Set `status: source_structured`.
5. Run:

```powershell
python scripts/validate_source_structure.py --source "<source_path>"
```

Do not tell the user the Capture-to-Source task is complete until this validation passes.

## Important Boundaries

- Do not delete user notes or raw captures unless explicitly asked.
- Do not store API keys inside the skill. Read them from the user's existing plugin settings or environment.
- Do not put plugin temp output in the main knowledge areas. Keep it under `_System`.
- Do not treat raw transcripts or OCR dumps as final Source notes.
- Do not report a Source as complete if it still has only `视频转录`, `图片 OCR`, `Transcript`, `内容`, or paragraph-only structure.
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
- Source structure validator: `scripts/validate_source_structure.py`
- Knowledge linking helper: `scripts/create_knowledge_note.py`
- Rule templates to copy into vaults: `assets/rules/`
