# Source Structuring

## Core Rule

Source is not a summary. Source is the readable, traceable version of source material.

Preserve the source's meaning, order, important claims, examples, and wording style. Improve only:

- semantic heading structure,
- paragraph boundaries,
- obvious ASR/OCR noise,
- navigation and traceability.

## Completion Gate

A Source note is not complete until all of these are true:

- frontmatter has `status: source_structured`;
- the note has at least three semantic `##` topic headings, unless the source is extremely short;
- generic headings such as `视频转录`, `图片 OCR`, `Transcript`, `内容`, `片段 1`, or `段落 1` have been replaced;
- long transcript blocks have been split into natural paragraphs;
- `scripts/validate_source_structure.py --source "<source_path>"` passes.

Do not report Capture-to-Source processing as done before this gate passes.

## Process

1. Read the full raw transcript, caption, or OCR first.
2. Identify the real topic blocks by meaning, not by character count.
3. Give each block a heading that tells the reader what this block is about.
4. Keep the original argument order unless there is a clear reason to reorder.
5. Split long text into natural paragraphs inside each heading.
6. Remove repeated filler words and obvious ASR fragments, but do not rewrite the source into your own essay.
7. Keep source links, raw links, platform, author, and capture references.
8. Add `Structure Tags`.
9. Leave durable extraction, comparison, and personal interpretation for Knowledge notes.

## Heading Standard

Good headings should summarize the topic of a block:

- `学生情况：专科背景，22 岁拿到字节高薪机会`
- `独立开发能力：面试官看重完整 AI 工具经验`
- `AI 自我迭代：Anthropic 把模型推到递归边缘`
- `Agent 降低门槛：复杂工具从安装教程变成自然语言任务`
- `端侧模型：苹果把隐私、硬件和本地 AI 放到同一条线上`

Bad headings are mechanical labels:

- `视频转录`
- `OCR 内容`
- `片段 1`
- `段落 2`
- `求职建议 3`

## Source vs Knowledge

Source keeps the source readable and traceable.

Knowledge extracts durable ideas, definitions, methods, comparisons, and personal understanding.
