# Folder Schema

## Principle

Separate capture, readable source material, distilled knowledge, rules, and machine output. This keeps phone capture lightweight while keeping the long-term vault clean.

## Folders

```text
00_Capture/
  External/YYYY-MM-DD/
  Personal/YYYY-MM-DD/

10_Sources/YYYY-MM-DD/

20_Knowledge/
  Concepts/
  Methods/
  Projects/
  Workflows/
  Media/

90_Rules/

_System/
  AnyContent/
    inbox/
    raw/
    media/
  Attachments/
  Plugin_Output/
  Logs/
```

## Meaning

`00_Capture` is for low-friction input. The user should be able to paste a link or write a rough note from a phone without thinking about metadata.

`10_Sources` is the real reading layer. It preserves source meaning while improving structure, headings, paragraphing, and traceability.

`20_Knowledge` is the distilled layer. Notes here should be clean, named by concept or method, and linked back to Sources.

`90_Rules` stores the workflow rules. Copy the skill's `assets/rules/*.md` into this folder during setup.

`_System` stores plugin output, raw transcripts, raw OCR, downloaded media, temporary files, and logs. It is not a knowledge area.

## Naming

Use concise English folder names. Date folders should use `YYYY-MM-DD`. Avoid numbering `_System`; it should visually signal machine space.
