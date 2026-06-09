# obsidian-source-wiki

An agent skill for building an Obsidian-based AI knowledge workflow.

It helps an agent set up and operate a vault with:

- `00_Capture` for low-friction daily capture
- `10_Sources` for structured source material
- `20_Knowledge` for distilled notes
- `90_Rules` for workflow rules
- `_System` for plugin output, raw transcripts, OCR, attachments, and logs

The skill also documents and automates parts of the media pipeline:

- Douyin video/image posts through AnyContent
- Xiaohongshu video transcription through the bundled adapter
- Xiaohongshu image OCR through the bundled adapter
- Source-to-Knowledge linking through a helper script

## Contents

```text
obsidian-source-wiki/
  SKILL.md
  agents/openai.yaml
  scripts/
  references/
  assets/rules/
```

## Install

Copy the `obsidian-source-wiki` folder into your Codex skills directory, for example:

Windows:

```text
%USERPROFILE%\.codex\skills\obsidian-source-wiki
```

macOS / Linux:

```text
~/.codex/skills/obsidian-source-wiki
```

Then ask your agent:

```text
Use obsidian-source-wiki to set up this Obsidian vault: <vault path>.
```

## Example Prompts

```text
Use obsidian-source-wiki to set up this Obsidian vault: D:\Obsidian\MyVault.
```

```text
Use obsidian-source-wiki to check whether this vault is ready for Douyin and Xiaohongshu media import: D:\Obsidian\MyVault.
```

```text
Use obsidian-source-wiki to process today's Capture links into Sources.
```

```text
Use obsidian-source-wiki to distill this Source into Knowledge: <source file>.
```

## Required External Setup

The skill can create folders and rules, but media import needs external setup:

- Obsidian desktop with Community plugins enabled
- AnyContent Vault Importer
- AnyContent backend at `http://127.0.0.1:8080`
- SiliconFlow account and API key in AnyContent settings
- `ffmpeg`
- Python package `requests`

Run:

```powershell
python obsidian-source-wiki/scripts/smoke_test.py
```

to verify the skill package without network or real API calls.

## Security

Do not commit API keys. This repository does not include any personal plugin settings or API keys. User API keys should stay in local Obsidian plugin settings or environment variables.

## License

MIT
