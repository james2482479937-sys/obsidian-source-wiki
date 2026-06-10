# Cleanup

## Goal

定期清理 Capture 区和 System 区，只保留文件夹框架，把处理完的内容删掉，减少噪音。

Source 区和 Knowledge 区不清理，长期保留。

## Capture 区清理规则

`00_Capture/External/` 和 `00_Capture/Personal/` 可以每天清理。

清理条件（必须同时满足）：

- 该文件已经生成对应 Source（`10_Sources/` 里存在）
- 对应 Source 的 `status` 为 `source_structured`
- 对应 Source 的 `capture_source` 字段已填写

不满足以上条件的 Capture 文件不删除。

清理后只保留文件夹框架：`00_Capture/External/` 和 `00_Capture/Personal/` 两个空文件夹。

## System 区清理规则

### 可以清理（每次处理完一批 Source 后）

- `_System/AnyContent/inbox/` — AnyContent 插件消费后的临时文件，全部可删
- `_System/AnyContent/media/` — 视频处理完后的临时音视频文件，全部可删
- `_System/Plugin_Output/XHS/` — XHS 插件输出，处理成 Source 后可删
- `_System/Logs/` — 日志文件，可定期清理

### 有条件清理

- `_System/AnyContent/raw/` — 只有对应 Source 的 `status: source_structured` 时才能删。raw 是 Source 重建的最后兜底，Source 未结构化前不能删。

### 不能随便清理

- `_System/Attachments/` — 图片等附件。如果有 Source 或 Knowledge 引用了某个文件，删了就断链。清理前必须确认没有引用。

## Source 区

`10_Sources` 长期保留，不自动清理。

Source 是原始素材保全区，不是临时缓存区。

## Knowledge 区

`20_Knowledge` 不自动清理。

只有在明确确认内容过时、重复或错误时，才允许人工调整。

## Safe Delete Rule

任何清理操作都必须先输出待删除文件列表，等用户确认后再执行。

没有用户确认，不执行删除。
