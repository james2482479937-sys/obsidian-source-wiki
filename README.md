# obsidian-source-wiki

一个给 Agent 使用的 Obsidian 知识库搭建 Skill。

它的目标不是把 Obsidian 变成一个复杂系统，而是让你的 Agent 帮你搭好一套稳定的知识流：

```text
Capture 随手记录
-> Source 结构化原材料
-> Knowledge 提炼后的知识
-> Rules 处理规则
-> _System 插件和脚本工作区
```

## 它能做什么

这个 Skill 可以帮助 Agent：

- 创建 Obsidian 知识库文件夹结构
- 安装并复制规则文档
- 检查 Obsidian 插件、API Key、ffmpeg、Python 环境
- 处理抖音视频和图文链接
- 处理小红书视频和图文链接
- 把视频转录、图片 OCR、网页内容整理成 Source
- 把 Source 进一步提炼成 Knowledge
- 自动维护 Source 和 Knowledge 的双向链接
- 对已经配置好环境的用户，一条命令处理 Capture 里的抖音/小红书链接

## 文件夹结构

```text
00_Capture/
  External/
  Personal/

10_Sources/

20_Knowledge/
  Concepts/
  Methods/
  Projects/
  Workflows/
  Media/

90_Rules/

_System/
  AnyContent/
  Attachments/
  Plugin_Output/
  Logs/
```

## 安装方式

把 `obsidian-source-wiki` 文件夹复制到你的 Codex skills 目录。

Windows:

```text
%USERPROFILE%\.codex\skills\obsidian-source-wiki
```

macOS / Linux:

```text
~/.codex/skills/obsidian-source-wiki
```

然后你可以对 Agent 说：

```text
Use obsidian-source-wiki to set up this Obsidian vault: <你的 Obsidian 仓库路径>
```

## 使用示例

初始化一个 Obsidian 仓库：

```text
Use obsidian-source-wiki to set up this Obsidian vault: D:\Obsidian\MyVault.
```

检查环境是否准备好：

```text
Use obsidian-source-wiki to check whether this vault is ready for Douyin and Xiaohongshu media import: D:\Obsidian\MyVault.
```

处理 Capture 里的链接：

```text
Use obsidian-source-wiki to process today's Capture links into Sources.
```

如果你的环境已经配置好，Agent 会优先使用统一入口：

```powershell
python obsidian-source-wiki/scripts/process_capture_links.py --vault "<vault>" --date YYYY-MM-DD --assume-ready
```

处理抖音等 AnyContent 链路时，这条统一命令会先检查 `http://127.0.0.1:8080`。如果后端没启动，并且本地已经有 `anycontent-obsidian-backend` 仓库和 `uv`，它会自动执行 `uv run python web/app.py` 启动后端。

注意：统一命令生成的是 Source 草稿。Agent 还必须把草稿改成带语义小标题的结构化 Source，并通过：

```powershell
python obsidian-source-wiki/scripts/validate_source_structure.py --source "<source_path>"
```

把 Source 提炼成 Knowledge：

```text
Use obsidian-source-wiki to distill this Source into Knowledge: <source file>.
```

## 需要提前准备什么

Skill 可以创建文件夹和规则，但媒体导入需要你自己准备这些东西：

- Obsidian 桌面端
- 开启 Obsidian Community plugins
- 安装 AnyContent Vault Importer
- 启动 AnyContent backend：`http://127.0.0.1:8080`
- 注册 SiliconFlow，并把 API Key 填进 AnyContent 设置
- 安装 `ffmpeg`
- Python 环境
- Python 包 `requests`

如果这些没准备好，Agent 会告诉你哪些链路暂时不能跑，例如：

- 抖音导入不能跑
- 小红书视频转录不能跑
- 小红书图片 OCR 不能跑

## 测试

不用真实 API，也可以先验证 Skill 包是否完整：

```powershell
python obsidian-source-wiki/scripts/smoke_test.py
```

看到下面结果说明基础结构没问题：

```text
smoke_test=ok
```

## 安全说明

这个仓库不包含任何个人 API Key，也不包含本地 Obsidian 插件配置。

用户自己的 API Key 应该只保存在本地 Obsidian 插件设置或环境变量里，不要提交到 GitHub。

## English

`obsidian-source-wiki` is an agent skill for building and operating an Obsidian-based AI knowledge workflow.

It helps an agent set up and run:

- `00_Capture` for low-friction daily capture
- `10_Sources` for structured source material
- `20_Knowledge` for distilled notes
- `90_Rules` for workflow rules
- `_System` for plugin output, raw transcripts, OCR, attachments, and logs

It also documents and automates parts of the media pipeline:

- Douyin video/image posts through AnyContent
- Xiaohongshu video transcription through the bundled adapter
- Xiaohongshu image OCR through the bundled adapter
- Source-to-Knowledge linking through a helper script

## License

MIT
