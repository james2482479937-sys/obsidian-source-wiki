---
name: ai-hot-article-pipeline
description: Use this skill when the user wants to turn today's AI HOT news into an article automatically. It fetches the AI HOT daily feed, creates a readable news report and candidate topic list, lets the agent choose the most discussable topic, then uses ai-article-generator to draft a Chinese article without default image or cover work.
---

# AI HOT Article Pipeline

把“今日 AI HOT 新闻”变成“可发布文章选题和正文”。

默认中文。默认不生成配图、封面或图片提示词，除非用户明确要求。

## Trigger

当用户说：

- `用今天 AI HOT 写一篇文章`
- `跑今日 AI 新闻并生成文章`
- `从今天 AI 热点里选题写文章`
- `AI HOT 选题生成文章`

执行本 skill。

## Paths

- AI HOT 日报目录：`C:\Users\24824\Documents\AI hot`
- 文章项目目录：`C:\Users\24824\Documents\写作`
- 文章生成 skill：`C:\Users\24824\Documents\写作\.codex\skills\ai-article-generator`
- 今日热点输出目录：`C:\Users\24824\Documents\写作\outputs\aihot`

## Workflow

### 1. 抓取今日 AI HOT

在 `C:\Users\24824\Documents\写作` 下运行：

```powershell
python .codex\skills\ai-hot-article-pipeline\scripts\fetch_aihot_daily.py --out-dir outputs\aihot --legacy-report "C:\Users\24824\Documents\AI hot\aihot-report.md"
```

脚本会生成：

- `outputs/aihot/YYYY-MM-DD_aihot_daily.md`：今日 AI HOT 中文日报。
- `outputs/aihot/YYYY-MM-DD_aihot_candidates.md`：文章选题候选池。
- `outputs/aihot/YYYY-MM-DD_aihot_raw.json`：原始结构化数据。
- 同步覆盖 `C:\Users\24824\Documents\AI hot\aihot-report.md`，兼容旧 AI HOT 日报流程。

如果抓取失败，先报告失败原因，不要编造今日新闻。

### 2. 从候选池里选文章主题

读取 `YYYY-MM-DD_aihot_candidates.md`，按下面标准选择 1 个主选题，最多给 2 个备选：

- 话题性：普通读者是否愿意点开、评论或转发。
- 争议性：是否有明确矛盾，例如效率 vs 风险、平台控制 vs 开放生态、人类岗位 vs AI agent。
- 与用户定位相关：优先选择 Agent、Codex、AI 产品、AI 工具、AI 工作流、普通人如何用 AI。
- 可写成长文：不能只是产品更新，要能延展出行业判断、方法论或普通人的行动建议。
- 证据足够：至少有 1 条明确来源链接；最好能引用同日报里的 2-3 条相关新闻互相支撑。

默认不要选纯模型参数、纯融资金额、纯论文细节，除非它能转化成普通人能理解的趋势判断。

### 3. 生成文章 Brief

把选定主题整理成一个写作 Brief，至少包含：

- 文章主题
- 选题理由
- 目标读者
- 核心判断
- 可引用的 AI HOT 新闻条目和链接
- 推荐标题 3-5 个
- 推荐大纲 1-2 套

如果用户没有要求“直接写完整文章”，先给用户确认标题和大纲。

### 4. 调用 ai-article-generator

用户确认后，使用 `ai-article-generator` 的正文交付流程：

- 生成 `outputs/{标题}_待审核.txt`
- 生成 `outputs/{标题}_待审核.md`
- 生成 `outputs/article_artifact_preview.html`
- 生成 `outputs/article_visual_paste.html`
- 启动或复用本地预览服务

正文默认不做配图。最终只追问：

```text
正文已完成。接下来你要不要我继续做：
1. 文章复检
2. 改写成另一平台版本
3. 两个都做
```

## Direct Mode

如果用户说“直接写”“全自动”“不用问我”，则跳过标题和大纲确认：

1. 抓今日 AI HOT。
2. 选择最有话题性的主题。
3. 自行确定标题和大纲。
4. 直接生成完整文章与本地预览。
5. 最终回复只给文件路径、预览链接、选题理由和剩余风险。

## Guardrails

- 不要把 AI HOT 日报当成唯一事实来源来做强断言。新闻细节来自日报，行业判断要写成“可以理解为”“更像是”“可能意味着”。
- 不要为了蹭热点夸大新闻影响。
- 不要默认生成图片、下载图片、做封面或写图片提示词。
- 不要把整篇文章塞满聊天窗口；正式正文必须落到本地文件。
