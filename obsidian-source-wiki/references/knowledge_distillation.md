# Knowledge Distillation

## Goal

Knowledge notes are the durable thinking layer. They should be clean, reusable, and linked back to Sources. They should not become a mixed dump or a simple summary of a Source.

The agent should extract stable ideas, concepts, methods, workflows, comparisons, and reusable judgments.

## Before Writing Knowledge

Read the structured Source first. Then decide whether the Source deserves:

- no Knowledge note: the Source is useful to keep, but has no reusable idea yet;
- one Knowledge note: the Source mainly supports one concept or method;
- multiple Knowledge notes: the Source contains distinct concepts, methods, projects, or workflows.

Do not create Knowledge notes just to mirror every Source.

## Folder Decision

Use these folders:

```text
20_Knowledge/Concepts/
20_Knowledge/Methods/
20_Knowledge/Projects/
20_Knowledge/Workflows/
20_Knowledge/Media/
```

Choose by function:

- `Concepts`: What is X? Use for definitions, mental models, roles, mechanisms, and named ideas.
- `Methods`: How to do X? Use for strategies, tactics, evaluation methods, operating principles.
- `Projects`: What concrete project/case/product is this? Use for specific examples worth tracking.
- `Workflows`: What repeatable process is this? Use for pipelines, setup flows, operating loops.
- `Media`: What book/video/creator/source collection is this? Use for media-level tracking.

## Naming

Use a concise Chinese title when the user's vault is Chinese. The title should name the reusable idea, not the source.

Good:

- `多Agent市场机制`
- `AI求职作品集策略`
- `Harness Engineering`
- `Obsidian媒体素材处理流程`

Avoid:

- `学习aiDay36总结`
- `这个视频的重点`
- `图文笔记1`
- `一些想法`

## Recommended Note Shapes

### Concepts

```markdown
# Concept Name

## 一句话定义

## 核心问题

## 关键机制

## 使用场景

## 与相关概念的区别

## 我的理解

## Source
```

### Methods

```markdown
# Method Name

## 适用场景

## 核心步骤

## 判断标准

## 常见误区

## 示例

## Source
```

### Workflows

```markdown
# Workflow Name

## 目标

## 输入

## 流程

## 输出

## 检查点

## Source
```

### Projects

```markdown
# Project Name

## 项目是什么

## 解决什么问题

## 关键设计

## 可借鉴点

## Source
```

## Linking

Every Knowledge note should link back to at least one Source.

When creating a Knowledge note from a Source, use:

```powershell
python scripts/create_knowledge_note.py --vault "<vault>" --source "<source-file>" --type Concepts --title "Concept Name"
```

Then fill the generated Knowledge note with the distilled content.

The script creates the Knowledge note and updates the Source frontmatter `knowledge_links` plus its `Linked Knowledge` section.

## Quality Checklist

Before finishing, check:

- The Knowledge note is not a paragraph-by-paragraph summary.
- The title names a reusable idea.
- The note has a clear hierarchy of headings.
- The note links back to Source.
- The Source links forward to Knowledge.
- The note belongs in the correct folder.
- No raw transcript/OCR dump is copied into Knowledge.
