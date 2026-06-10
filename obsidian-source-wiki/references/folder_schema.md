# Folder Schema

## Principle

Separate capture, readable source material, distilled knowledge, rules, and machine output. This keeps phone capture lightweight while keeping the long-term vault clean.

## Folders

```text
00_Capture/
  External/       ← 外部内容：抖音、小红书链接等，随手丢，不命名也没关系
  Personal/       ← 个人随记：碎点子、灵感、随手记录

10_Sources/
  YYYY-MM-DD/     ← 按处理日期归档的结构化原始素材

20_Knowledge/
  External/       ← 来自外部内容（视频、图文）提炼的知识
  Personal/       ← 来自个人随记、碎点子提炼的知识

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

`00_Capture` is for zero-friction input. Files do not need names or dates. Drop a link or a rough idea and let the agent handle the rest. The two subfolders signal origin type, not content category.

`10_Sources` is the real reading layer. It preserves source meaning while improving structure, headings, paragraphing, and traceability. Every Source file records `capture_source: external` or `capture_source: personal` in its frontmatter so the origin is never lost even after Capture is cleaned up.

`20_Knowledge` is the distilled layer. Notes here should be clean, named by concept, and linked back to Sources. `External/` holds knowledge from videos, articles, and other outside content. `Personal/` holds knowledge distilled from the user's own ideas and notes. The agent decides which folder based on the Source's `capture_source` field — never based on whether the original Capture file still exists.

`90_Rules` stores the workflow rules. Copy the skill's `assets/rules/*.md` into this folder during setup.

`_System` stores plugin output, raw transcripts, raw OCR, downloaded media, temporary files, and logs. It is not a knowledge area.

## Naming

Files in `00_Capture` do not need names. The agent reads content, not filenames.

Source files in `10_Sources/YYYY-MM-DD/` should be named after the topic for traceability.

Knowledge files in `20_Knowledge/External/` and `20_Knowledge/Personal/` should be named by concept or method, not by date.
