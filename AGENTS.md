# 写作项目说明

默认中文回答。本项目统一处理所有写作相关任务：AI 文章生成、AI 日报、寓言故事、Obsidian 知识库。

---

## 意图 → Skill 速查

| 用户说的意思 | 调用的 Skill |
|---|---|
| 处理链接 / 今天的新内容 / 处理 capture / 抖音小红书转写 / Obsidian 入库 / 转成 Source | `obsidian-source-wiki` |
| 总结/整理 capture-personal / 今天的灵感随记 | `obsidian-source-wiki` |
| 帮我记一个灵感 / 我刚才想到… / 记到 obsidian | `obsidian-source-wiki` |
| AI HOT 选题写文章 / 今日新闻写文章 / 跑 AI HOT | `ai-hot-article-pipeline` |
| 这篇参考文章 + 这个主题 → 生成正文 | `ai-article-generator` |
| 写一个寓言 / 用寓言解释概念 / 今日寓言 | `fable-concept-writer` |

**关键规则：** 任何包含"链接"、"处理"、"转写"、"Obsidian"、"capture"、"Source"、"灵感"的请求，第一反应是 `obsidian-source-wiki`，不是文章生成。

---

## Obsidian / 链接 / 灵感处理

触发词（任意一条）：

- `处理新链接` / `处理今天的新内容` / `Obsidian 链接转写`
- `把 capture 里的内容处理一下` / `转成 Source` / `视频转录到 Source`
- `小红书/抖音链接处理`
- `总结今天的灵感` / `整理 capture-personal`
- `帮我记一个灵感` / `我有个想法：` / `记到 obsidian`

必须走：`.codex\skills\obsidian-source-wiki`

不要进入文章生成 skill，不要只输出普通 Markdown。

第一动作：在本项目根目录运行：

```powershell
python ".codex\skills\obsidian-source-wiki\scripts\process_obsidian_capture.py"
```

如果用户指定 Capture 文件：

```powershell
python ".codex\skills\obsidian-source-wiki\scripts\process_obsidian_capture.py" --capture-file "<capture-file>"
```

脚本输出 `source_paths` 后，继续做语义小标题、自然段结构化和结构校验。校验通过前不要汇报完成。

---

## AI HOT 选题写文章

触发词：

- `用今天 AI HOT 写一篇文章`
- `今日 AI 新闻选题写文章`
- `跑今日 AI HOT 并生成文章`
- `从今天热点里挑一个主题写文章`

使用：`.codex\skills\ai-hot-article-pipeline`

执行顺序：

1. 抓取今日 AI HOT 日报。
2. 生成今日候选选题池。
3. 选择最有话题性的文章主题。
4. 整理标题和大纲。
5. 如果用户说"直接写/全自动"，直接生成完整文章；否则先让用户确认标题和大纲。
6. 调用 `ai-article-generator` 生成本地正文和 HTML 预览。

---

## 参考文章 + 主题 → 生成正文

触发词：

- `用这篇文章 + 这个主题写一篇`
- `参考这篇，写关于 XX 的文章`
- `文章生成`

使用：`.codex\skills\ai-article-generator`

---

## 寓言故事

触发词：

- `写一个寓言` / `今日寓言` / `用寓言解释 XX` / `寓言写作`

使用：`.codex\skills\fable-concept-writer`

---

## 配图规则

默认不生成配图、封面、图片提示词，也不下载图片。只有用户明确说"生成配图""做封面""给图片提示词"时才处理。

## 输出要求

正式正文必须落到 `outputs/`，不要只在聊天里输出。

最终回复只汇报：改了什么文件、验证结果、剩余风险。
