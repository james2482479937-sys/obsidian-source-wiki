# Sources to Knowledge

## Goal

把 `10_Sources` 里的结构化素材，提炼成 `20_Knowledge` 里的长期知识文件。

这一步才进行价值判断、总结提炼、概念归纳和双向链接。

## Input

- `10_Sources/YYYY-MM-DD/`

## Output

- `20_Knowledge/External/`  ← 来自外部内容（视频、图文）的知识提炼
- `20_Knowledge/Personal/`  ← 来自个人随记、碎点子的知识提炼

## 如何判断放 External 还是 Personal

**唯一判断依据是 Source 文件的 `capture_source` 字段，不依赖 Capture 文件是否还存在。**

```yaml
capture_source: external  →  Knowledge/External/
capture_source: personal  →  Knowledge/Personal/
```

如果 Source 缺少 `capture_source` 字段，先补上再提炼，不要猜测。

## Knowledge Rules

- 每个 Knowledge 文件只围绕一个核心主题。
- 先写一句话结论。
- 内容必须结构清晰，优先使用一级、二级、三级标题。
- 只保留可复用观点，不保留流水账。
- 能变成方法论、判断标准、项目经验、概念解释的内容才进入 Knowledge。
- 必须保留来源链接，方便追溯。
- 能链接已有笔记时，使用 Obsidian 双向链接。
- 不确定的判断标记为 `draft`。
- 不要把无标点转录原文复制进 Knowledge。
- 不要让一个 Knowledge 文件同时塞入多个不相关主题。

## Required Structure

每个 Knowledge 文件建议使用：

```markdown
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

# 标题

## 一句话结论

## 1. 背景

### 1.1 问题从哪里来

### 1.2 为什么值得记录

## 2. 核心观点

### 2.1 观点一

### 2.2 观点二

## 3. 我的判断

### 3.1 适用场景

### 3.2 不适用场景

## 4. 可复用规则

## 5. 例子

## 6. 来源与关联
```

## Source Linking

Knowledge 文件必须链接回 Source。

示例：

```yaml
sources:
  - "[[10_Sources/2026-06-10/example-source]]"
related:
  - "[[相关知识文件]]"
```

如果 Source 文件已经生成 Knowledge，也可以在 Source 文件的 `knowledge_links` 中补回链接。

## Mindmap Compatibility

为了方便思维导图插件渲染，Knowledge 文件标题层级要稳定：

- `#` 只用于文件主标题。
- `##` 用于主要模块。
- `###` 用于模块下的具体观点。
- 不要跳级使用标题。
