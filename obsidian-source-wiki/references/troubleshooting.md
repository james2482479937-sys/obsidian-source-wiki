# Troubleshooting

## AnyContent Creates Raw But Script Fails

Console output may fail on Windows if filenames contain emoji or Chinese characters. Check `_System/AnyContent/raw` and `10_Sources/YYYY-MM-DD` before rerunning.

## Xiaohongshu OCR Fails

Check whether the API key has balance and access to a vision model. If the first image returns insufficient balance, do not keep retrying every image.

The tested failure text was `account balance is insufficient`. In that case, mark the Source `needs_ocr` or ask the user to recharge/configure a usable OCR provider, then rerun the adapter.

If parsing fails, open the resolved Xiaohongshu page and inspect whether `window.__INITIAL_STATE__` still contains `noteDetailMap`.

## Video Download Fails

Retry with resumable download if possible. Xiaohongshu CDN can break mid-stream. Temporary media should remain under `_System/AnyContent/media` and be deleted after success.

## Obsidian Plugins Create Extra Folders

Patch plugin settings to put output under `_System`. If a plugin still creates a root folder, move only after verifying the plugin will not break, or leave it and document why.

## Agent 重复处理已有 Source（最常见错误）

**症状**：Source 草稿生成后发现 `10_Sources/YYYY-MM-DD/` 里同名文件已存在，或处理了昨天的 Capture 文件而非今天的新增内容。

**根本原因**：Agent 看到 Capture 文件夹就直接处理，没有先比对现有 Source。

**正确操作——处理前必须执行的比对步骤**：

```powershell
# 1. 列出所有 Source 日期文件夹，确认哪些已处理
Get-ChildItem "vault\10_Sources" -Directory | Sort-Object Name

# 2. 列出对应日期的已有 Source 文件名
Get-ChildItem "vault\10_Sources\YYYY-MM-DD" -File | Select-Object Name

# 3. 列出 Capture 文件夹里所有待处理文件（按修改时间排序找最新）
Get-ChildItem "vault\00_Capture\External" -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object -First 20 FullName, LastWriteTime
```

**判断规则**：
- Capture 文件的日期文件夹已存在对应 Source 文件夹且文件数量吻合 → 该 Capture 文件夹已处理，跳过
- Capture 文件夹里有文件但 Source 里找不到对应内容 → 才是真正需要处理的
- 没有日期文件夹的 Capture 文件（如"未命名.md"）→ 优先处理，通常是今天最新的

**不能只靠文件夹日期判断**：Capture 文件日期是内容创建日，脚本运行日期不一定和它一致，要以 Source 文件是否存在为准。

## AnyContent 多视频同时入队导致 raw 映射混乱

**症状**：一个 Capture 文件里有 4 条抖音链接，脚本只生成了 2 个 Source，另外 2 条视频的 raw 已下载但没有对应 Source。或者 Source 内容对不上视频（A 的内容写进了 B 的文件里）。

**根本原因**：AnyContent backend 有时会把多视频请求的 raw 输出顺序打乱，或返回缓存结果，导致脚本的"第 N 条链接 → 第 N 个 raw"映射失效。

**排查步骤**：

```powershell
# 查看 raw 文件夹里已下载了哪些视频
Get-ChildItem "vault\_System\AnyContent\raw" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 10 Name
```

对比 raw 文件名和 Capture 里的链接描述，找出：
- 已有 raw 但没有 Source 的 → 手动从 raw 创建 Source
- Source 内容和 raw 不一致的 → 以 raw 内容为准，重新结构化

**处理原则**：raw 文件夹是真实下载凭证，Source 内容应与对应 raw 完全一致。一旦发现映射混乱，先核查全部 raw，再逐一创建缺失 Source。

## Source Looks Too Mechanical

The script generated only a draft. The agent must run the semantic structuring pass from `source_structuring.md`.

## Knowledge Note Is Not Linked Back

Use `scripts/create_knowledge_note.py` instead of manually creating a Knowledge file. It creates the Knowledge scaffold and updates the Source note's `knowledge_links` plus `Linked Knowledge` section.
