# Principles

## Core Structure

这个仓库分为四层：

- `00_Capture`：手机和电脑的轻量记录入口，不要求结构完整。
- `10_Sources`：资料保全区，把原始材料整理成可阅读、可追溯的结构化版本。
- `20_Knowledge`：知识沉淀区，只保留可复用的结论、概念、方法和项目经验。
- `90_Rules`：处理规则区，约束 AI 如何整理、提炼、命名和清理文件。
- `_System`：机器工作区，存放插件输出、中间文件、附件、日志和自动化缓存。

## Core Principle

记录时不要增加负担，整理时再增加结构。

`00_Capture` 负责低成本捕获，`10_Sources` 负责保真和结构化，`20_Knowledge` 负责提炼和链接。

`_System` 不属于知识库主体，平时不作为阅读和整理对象。

除非规则明确要求，AI 不应把 `_System` 里的内容直接当作 Knowledge。

## Personal and External

`00_Capture/Personal` 放自己的灵感、随手想法、情绪、判断和生活片段。

`00_Capture/External` 放他人的内容，例如文章、视频、播客、网页、转录稿和课程材料。

Personal 默认保留原话，不自动删除。

External 默认作为知识沉淀素材，处理完成后可以归档或清理，但不能在没有生成 Source 或 Knowledge 前删除。

## AI Processing

AI 处理时不要一次读取整个仓库。

优先按以下范围处理：

1. 指定日期。
2. 指定文件夹。
3. 指定主题。
4. 指定文件。

## Knowledge Standard

`20_Knowledge` 不是资料堆放区。

只有以后可能复用、能形成判断、方法、概念或项目经验的内容，才进入 `20_Knowledge`。
