# Sources to Knowledge

## Goal

把 `10_Sources` 里的结构化素材，提炼成 `20_Knowledge` 里的长期知识文件。

这一步才进行价值判断、总结提炼、概念归纳和双向链接。

## Input

- `10_Sources/YYYY-MM-DD/`，只处理 `knowledge_status: pending` 的文件

**每次提炼前，先扫 pending，不要全量读取所有 Source：**

```powershell
Select-String -Path "vault\10_Sources\**\*.md" -Pattern "^knowledge_status: pending" | Select-Object Path
```

处理完一个 Source 后，立即把该文件的 `knowledge_status` 改为 `done`。

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

## Token 效率：分层阅读，不默认全文读取

Source 文件分三层，按需读取：

| 层 | 内容 | 何时读 |
|----|------|--------|
| `Structure Tags` | 主题、人物、概念、场景（几十 token） | **每次都先读这一层**，判断值不值得提炼、提炼成什么 |
| 语义小标题区 | H2 标题 + 每段首句（几百 token） | 决定提炼后，读这一层确定结构和观点 |
| 原始转录 / OCR | 完整逐字内容（可能几千 token） | 只在需要引用原话时才读 |

**不要默认全文读 Source。** 先读 `Structure Tags`，够用就够用。

## 什么值得提炼

只有一条标准：**下次遇到类似情况时，我会想起来用这个吗？**

| 值得提炼 | 不值得提炼 |
|---------|-----------|
| 可以复用的判断标准或方法 | 纯信息/新闻（某模型发布了） |
| 让你改变做法的具体操作 | 已经知道的事情 |
| 之前没想到的视角 | 一次性的事实 |
| 自己的延伸思考或反应 | 流水账内容摘要 |

## 提炼成什么形态

根据提炼出来的类型决定形态，不强制套固定模板：

| 类型 | 形态 |
|------|------|
| 一个原则 | "在 X 情况下，做 Y，因为 Z" |
| 一个方法 | 步骤或决策树 |
| 一个视角 | 你的立场 + 为什么同意或不同意 |
| 一个连接 | 这和已有某个知识的关系 |

## Knowledge 文件模板

**标题写成一个可以被反驳的陈述，不要写成话题词。**

好标题：`用 43 行 skill 文件就能让 AI coding 界面质量上一个台阶`
差标题：`Design Skill 总结`

**只写有内容的部分，没有就不写，不要强制填空标题。**

```markdown
---
title:
created:
capture_source: external   # 或 personal
status: draft
sources: []
---

# 标题（一个可以被反驳的陈述）

## 核心洞察

一两句话。看完这里就够了。

## 为什么这样说

支撑洞察的关键论据，3-5 条，不需要面面俱到。

## 怎么用

具体在什么场景下调用这个知识。没有就不写这一节。

## 来源

[[10_Sources/YYYY-MM-DD/source-file]]
```

## Source Linking

Knowledge 文件必须链接回 Source，写在 frontmatter 和正文来源区：

```yaml
sources:
  - "[[10_Sources/2026-06-10/example-source]]"
```

如果 Source 文件已经生成 Knowledge，也可以在 Source 文件的 `knowledge_links` 中补回链接。
