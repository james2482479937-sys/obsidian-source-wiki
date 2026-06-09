# Plugin Setup

## Agent Responsibility During Setup

When setting up a new vault, explicitly tell the user that folder creation is only the first step. Media import will not work until the required Obsidian plugin, backend service, API key, and local tools are ready.

After running `scripts/setup_vault.py`, always run `scripts/check_environment.py` and summarize missing requirements.

## Required Plugin

AnyContent Vault Importer is required for:

- Douyin/TikTok/WeChat/YouTube import,
- Douyin image-post OCR through AnyContent,
- storing the SiliconFlow/SenseVoice API key used by scripts.

Why it matters: it is the bridge from share links to raw Obsidian notes for Douyin and other supported platforms. It also provides the API key location reused by the Xiaohongshu adapter.

The user must install and enable it manually in Obsidian if it is missing. The agent may configure its settings only after the plugin folder exists.

Recommended settings:

```text
Backend URL: http://127.0.0.1:8080
Raw folder: _System/AnyContent/raw
Inbox folder: _System/AnyContent/inbox
Inbox auto-consume: on
Media subfolder: media
Save no-watermark video locally: off
```

## Required Account and API Key

The user needs a SiliconFlow account and API key if they want:

- video speech-to-text,
- Xiaohongshu video transcription,
- Xiaohongshu image OCR,
- image-post OCR when using the adapter.

Why it matters: SiliconFlow provides the speech-to-text and vision OCR models used by the current workflow.

The API key should be entered in the AnyContent Vault Importer settings. Do not paste or save the user's API key into skill files.

If the key is missing or has no balance, report that media import is not ready. Do not pretend the workflow is complete.

The bundled Xiaohongshu adapter currently uses:

- ASR: `FunAudioLLM/SenseVoiceSmall`
- OCR fallback list: Qwen VL / Qwen Omni vision-capable models configured in `scripts/xhs_to_source.py`

The user's SiliconFlow account must have access and balance for the selected ASR/OCR models. If OCR returns `account balance is insufficient`, stop and ask the user to recharge or configure a usable OCR provider.

## Required Backend and Local Tools

AnyContent backend should be running at:

```text
http://127.0.0.1:8080
```

`ffmpeg` is required for Xiaohongshu video processing because the adapter extracts audio from temporary video files.

Why it matters: Xiaohongshu is not directly handled by AnyContent in this workflow, so the adapter has to extract audio before sending it to ASR.

Python is required to run the bundled scripts. If a script reports a missing Python package, install only the required package and explain the scope to the user.

The Xiaohongshu adapter requires the Python package `requests`.

## Optional Plugins

XHS Importer can help with Xiaohongshu clipping, but the skill's `xhs_to_source.py` is the main adapter for Xiaohongshu video and image posts.

Mind Elixir Mind Map can render structured Markdown headings into mind maps.

QuickAdd can make phone/desktop capture shortcuts easier.

Excalidraw is useful for diagrams and sketches.

## Safety

Community plugin installation usually requires manual confirmation inside Obsidian. The agent can inspect and patch plugin settings if plugins already exist, but should not claim it has fully installed plugins unless verified on disk.

Do not store API keys inside the skill files. Use the user's AnyContent plugin settings or environment variables.

## User-Facing Setup Checklist

When reporting setup status, use this shape:

```text
Already created:
- folder system
- rules
- _System workspace

You still need to install/register:
- AnyContent Vault Importer
- SiliconFlow account and API key
- AnyContent backend at http://127.0.0.1:8080
- ffmpeg
- Python package requests

Until those are done:
- Douyin import will not work
- Xiaohongshu video transcription will not work
- Xiaohongshu image OCR will not work
```
