# obsidian-source-wiki

这是一个结合多个 AI Skill 的个人知识收藏与写作工作流。

它不只是单独的 Obsidian 入库工具，也不是单独的文章生成器，而是把“收藏、转写、整理、选题、写作、寓言化表达”放在同一个项目里：先把外部内容和灵感稳定沉淀到 Obsidian，再从 AI 热点、参考文章或概念出发生成可审核、可复制的写作产物。

## 这个项目解决什么

日常使用时，它覆盖两条主线：

- 知识收藏：处理 Obsidian Capture、外部链接、抖音/小红书/视频/图片内容，把原始材料整理成 Source，再进入 Knowledge 工作流。
- 写作生产：从 AI HOT 热点、参考文章或指定概念出发，生成文章选题、正文、本地预览页或寓言故事。

所以它实际是一个“写作和收藏共存”的 Skill 项目：`obsidian-source-wiki` 负责收藏入口，`ai-hot-article-pipeline`、`ai-article-generator` 和 `fable-concept-writer` 负责写作出口。

## 包含的 Skills

| Skill | 用途 |
|---|---|
| `obsidian-source-wiki` | Obsidian Capture、链接转写、Source 结构化、灵感入库、知识整理 |
| `ai-hot-article-pipeline` | 抓取今日 AI HOT，生成日报、候选选题，并串联文章生成 |
| `ai-article-generator` | 根据参考文章和主题生成中文长文、本地预览页和可复制正文 |
| `fable-concept-writer` | 用寓言解释跨学科高阶概念，并保存为本地 Markdown 产物 |

## 推荐使用方式

如果你只需要 Obsidian 知识库搭建和链接入库，使用：

```text
Use obsidian-source-wiki to process today's Capture links into Sources.
```

如果你想从当天 AI 热点里选题写文章，使用：

```text
Use ai-hot-article-pipeline to fetch today's AI HOT news and generate a Chinese article.
```

如果你已经有参考文章和主题，使用：

```text
Use ai-article-generator to turn this reference article and topic into a Chinese article.
```

如果你想用寓言解释一个概念，使用：

```text
Use fable-concept-writer to write a fable about this concept.
```

## 本地项目路由

本仓库同时保留 `AGENTS.md`，用于说明在本地写作项目里如何根据用户意图选择 skill。核心规则是：

- 包含“链接、处理、转写、Obsidian、capture、Source、灵感”的请求，优先进入 `obsidian-source-wiki`。
- 包含“AI HOT、今日新闻、热点选题、生成文章”的请求，进入 `ai-hot-article-pipeline`。
- 包含“参考文章 + 主题”的请求，进入 `ai-article-generator`。
- 包含“寓言、用寓言解释概念、今日寓言”的请求，进入 `fable-concept-writer`。

## 安装方式

把需要的 skill 文件夹复制到你的 Codex skills 目录：

Windows:

```text
%USERPROFILE%\.codex\skills\<skill-name>
```

macOS / Linux:

```text
~/.codex/skills/<skill-name>
```

如果要在一个写作项目里组合使用这些 skill，可以把本仓库的 `AGENTS.md` 放到项目根目录，再把需要的 skill 放到项目内 `.codex/skills/`。

## 文件结构

```text
.
├─ AGENTS.md
├─ obsidian-source-wiki/
├─ ai-hot-article-pipeline/
├─ ai-article-generator/
└─ fable-concept-writer/
```

## 安全说明

这个仓库不应该包含个人 API Key、真实账号 token、本地私密配置或未准备公开的文章草稿。`outputs/` 下的具体产物属于本地交付结果，默认不提交到 GitHub。

## License

MIT
