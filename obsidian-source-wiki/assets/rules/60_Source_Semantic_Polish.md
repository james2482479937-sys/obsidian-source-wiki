# Source Semantic Polish

完整结构化规范见：[[70_Source_Article_Structuring]]

## Goal

把 AnyContent、OCR 或 ASR 生成的初步 Source，整理成适合回溯阅读的结构化 Source。

这一步发生在 Source 阶段，不是 Knowledge 阶段。

## Core Rule

Source 的目标是“读起来清楚”，不是“总结成观点”。

整理时要保留原文信息量，只改变阅读结构：

- 更准确的小标题
- 更自然的段落
- 更清楚的话题切换
- 更少的口语噪音

## Workflow

1. 先通读转录稿，识别发言的自然环节。
2. 按连续主题切成若干大段。
3. 给每个大段写一个能概括内容的小标题。
4. 小标题下面继续按自然段拆开。
5. 保留原始来源、作者、链接、Source Info 和 Linked Knowledge。
6. 不做深度总结，不把内容改写成 Knowledge。

## Good Headings

好的 Source 小标题应该像这样：

- 学生情况：专科背景，22 岁拿到字节高薪机会
- 独立开发能力：面试官真正看重的是完整 AI 工具经验
- 项目完整度：三端上线和真实问题处理形成主要加分项
- 招聘趋势：项目能力正在超过学历背景
- 项目选题：从真实商业场景里找 AI 应用
- 闲聊补充：Codex 订阅和礼品卡价格

## Bad Headings

不要使用：

- 片段 1
- 片段 2
- 求职建议 3
- 面试价值 4
- 学生案例 5

这类标题没有阅读价值，只说明机器切过段。

## Paragraph Rules

- 每个小标题下面通常放 1 到 5 个自然段。
- 每个自然段通常 2 到 4 句。
- 一段只承载一个局部意思。
- 如果同一小标题下出现新话题，要拆成新的小标题。

## Boundary

允许：

- 补标点
- 调整换行
- 删除明显无意义语气词
- 修正很明显的 ASR 识别错词
- 添加语义小标题

不允许：

- 删除关键信息
- 把原文压缩成摘要
- 加入来源中没有的新观点
- 把 Source 写成方法论文章

## Skill Note

后续如果做成 skill，流程应固定为：

```text
Capture
↓
AnyContent / OCR / ASR 生成初稿 Source
↓
Source Semantic Polish
↓
Knowledge 提炼
```
