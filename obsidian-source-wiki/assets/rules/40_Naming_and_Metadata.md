# Naming and Metadata

## Folder Naming

Capture 使用：

```text
00_Capture/Personal/YYYY-MM-DD/
00_Capture/External/YYYY-MM-DD/
```

Sources 使用：

```text
10_Sources/YYYY-MM-DD/
```

Knowledge 按主题分类，不按日期分类：

```text
20_Knowledge/Concepts/
20_Knowledge/Methods/
20_Knowledge/Projects/
20_Knowledge/Workflows/
20_Knowledge/Media/
```

System 使用：

```text
_System/AnyContent/inbox/
_System/AnyContent/raw/
_System/AnyContent/media/
_System/Attachments/
_System/Plugin_Output/
_System/Logs/
```

`_System` 只放机器生成物和处理过程文件，不放正式知识文件。

## Capture Naming

Capture 文件名尽量简单：

```text
HHMM-short-title.md
```

例子：

```text
0930-obsidian-feeling.md
1420-karpathy-video.md
```

## Source Naming

Source 文件名使用清晰主题：

```text
obsidian-ai-workflow.md
karpathy-llm-wiki-video.md
```

## Knowledge Naming

Knowledge 文件名使用可复用主题：

```text
mobile-obsidian-as-capture.md
capture-source-knowledge-system.md
```

## Capture Metadata

Capture 阶段不强制填写属性。

手机记录时，只要放对文件夹即可：

- 自己的想法放 `Personal`。
- 他人的内容放 `External`。

## Source Metadata

Source 建议使用：

```yaml
---
title:
created:
source_type:
platform:
author:
source_url:
saved_at:
status: structured
tags: []
knowledge_links: []
---
```

## Knowledge Metadata

Knowledge 建议使用：

```yaml
---
title:
created:
updated:
type:
status: draft
tags: []
sources: []
related: []
---
```

## Status Values

常用状态：

- `raw`：原始捕获。
- `structured`：已经结构化。
- `draft`：已经提炼，但仍需验证。
- `evergreen`：长期稳定可复用。
- `archived`：已归档，不主动处理。
