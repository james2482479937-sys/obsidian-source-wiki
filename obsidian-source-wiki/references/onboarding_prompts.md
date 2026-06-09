# Onboarding Prompts

Use these prompts to help a user or another agent operate the skill.

## First-Time Vault Setup

```text
Use obsidian-source-wiki to set up this Obsidian vault: <vault path>. Create the folder and rules system, then check which plugins, API keys, backend services, and local tools are still missing.
```

Expected agent behavior:

- create folders and rules,
- run environment checks,
- tell the user which requirements are missing,
- avoid claiming the media workflow is ready until checks pass.

## Environment Check

```text
Use obsidian-source-wiki to check whether this vault is ready for Douyin and Xiaohongshu media import: <vault path>.
```

Expected agent behavior:

- run `check_environment.py`,
- report missing AnyContent, SiliconFlow API key, backend, ffmpeg, Python, and requests,
- explain which media routes are blocked.

## Process Capture Links

```text
Use obsidian-source-wiki to process today's Capture links into Sources.
```

Expected agent behavior:

- inspect the Capture folder,
- route Douyin links through AnyContent,
- route Xiaohongshu links through `xhs_to_source.py`,
- save images only when the capture text explicitly asks for it,
- polish raw output into structured Source notes.

## Distill Source Into Knowledge

```text
Use obsidian-source-wiki to distill this Source into Knowledge: <source file>.
```

Expected agent behavior:

- read `knowledge_distillation.md`,
- decide whether to create zero, one, or multiple Knowledge notes,
- use `create_knowledge_note.py` for each note,
- fill the generated note with distilled content,
- verify Source and Knowledge link to each other.

## Troubleshoot

```text
Use obsidian-source-wiki to diagnose why media import failed in this vault: <vault path>.
```

Expected agent behavior:

- check environment,
- inspect `_System/AnyContent/raw`,
- look for API balance errors,
- look for console encoding issues,
- report the next concrete fix.
