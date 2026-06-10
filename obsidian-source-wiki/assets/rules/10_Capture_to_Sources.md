# Capture to Sources

## Goal

把 `00_Capture` 里的零散记录整理成 `10_Sources` 里的结构化素材文件。

这一步只做保全和结构化，不做深度总结，不替用户判断哪些观点最有价值。

## Input

- `00_Capture/Personal/YYYY-MM-DD/`
- `00_Capture/External/YYYY-MM-DD/`

## Output

- `10_Sources/YYYY-MM-DD/`

## 处理前必须先比对现有 Source（最容易犯错的步骤）

**不要看到 Capture 文件就直接处理。** Capture 文件的日期 ≠ 未处理，必须先确认 Source 里有没有对应文件。

```powershell
# 1. 确认哪些日期已有 Source
Get-ChildItem "vault\10_Sources" -Directory | Sort-Object Name

# 2. 查看已有 Source 文件列表
Get-ChildItem "vault\10_Sources\YYYY-MM-DD" -File | Select-Object Name

# 3. 找最新 Capture 文件（没有日期文件夹的优先处理）
Get-ChildItem "vault\00_Capture\External" -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object -First 20 FullName, LastWriteTime
```

判断规则：
- Capture 对应的 Source 已存在 → 跳过，不重复处理
- 没有日期子文件夹的 Capture 文件（如"未命名.md"）→ 通常是今天最新的，优先处理
- Source 里找不到对应文件 → 才是真正需要处理的

## General Rules

- 同一天同一主题的内容可以合并成一个 Source 文件。
- 不同主题必须拆成不同 Source 文件。
- Source 文件要让以后阅读更省力。
- Source 文件不能丢失来源信息。
- 不要在 Source 阶段做深度观点提炼。
- 不要把 Source 写成 Knowledge。

## Personal Capture Rules

Personal 内容必须完全保留原话。

允许补充：

- 标题
- 创建时间
- 来源路径
- 简短背景
- 标签

不允许：

- 改写原话
- 润色原话
- 删除原话
- 把原话直接总结替代

如果需要整理，只能在原话之外新增说明区。

## External Capture Rules

External 内容不做价值筛选，只做结构清洗。

文章类内容：

- 尽量保留原文快照，防止原链接失效。
- 可以补标题层级。
- 可以整理段落。
- 可以修正明显的排版问题。
- 不要修改作者原意。

视频、播客、转录类内容：

- 补标点。
- 分段。
- 区分说话人。
- 去除明显多余的语气词，例如“嗯”“啊”“呃”。
- 保留来源链接、作者、平台和保存时间。
- 添加主题标签、人物标签和内容类型标签。
- 不要因为 AI 判断“价值不高”而删除内容。

## Semantic Structure Rules

Source 是以后回溯原内容时真正阅读的版本，因此转录稿必须做语义结构化。

详细执行规范见：[[70_Source_Article_Structuring]]

小标题规则：

- 小标题要概括这一大段在讲什么，不能使用“片段 1”“求职建议 2”“面试价值 3”这类机械标题。
- 一个小标题只覆盖一个连续主题。
- 话题切到下个环节时，必须新建小标题。
- 小标题应保留原内容的阅读线索，例如“学生情况：专科背景，22 岁拿到高薪机会”。
- 不要把小标题写成 Knowledge 总结，Source 小标题只负责帮助回看原文。

自然段规则：

- 每个小标题下面继续按自然段切分。
- 每个自然段通常保留 2 到 4 句。
- 一个自然段只表达一个局部意思。
- 不要把整段转录堆成一大块。

处理边界：

- 可以修正明显口误、重复词和无意义语气词。
- 可以补标点、换行、加小标题。
- 不要改变作者原意。
- 不要把原文压缩成摘要。
- 深度提炼、观点判断和方法论归纳放到 Knowledge 阶段。

## Source File Structure

每个 Source 文件建议包含：

```markdown
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

# 标题

## Source Info

## Background

## Reading Version

## Structure Tags

## Linked Knowledge
```

## Boundary

Source 只负责清洗和保真。

Knowledge 才负责筛选、提炼、判断和复用。
