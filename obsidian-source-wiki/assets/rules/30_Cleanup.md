# Cleanup

## Goal

清理规则的目标是减少噪音，但不能误删有记忆价值或溯源价值的内容。

## Personal Capture

`00_Capture/Personal` 下的内容默认保留。

即使已经处理成 Source 或 Knowledge，也不要自动删除。

如果需要清理，只能人工决定。

## External Capture

`00_Capture/External` 下的内容默认是待处理素材。

可以清理，但必须同时满足：

- 已经生成对应 Source 或 Knowledge。
- 原始链接已经保留。
- 有价值内容已经完成结构化保存。
- 文件不是用户特别标记要保留的内容。

如果不确定，不删除。

## Sources

`10_Sources` 默认长期保留。

Source 是资料保全区，不是临时缓存区。

如果 Source 已经完整沉淀成 Knowledge，可以标记为 `archived`，但不要自动删除。

## Knowledge

`20_Knowledge` 不自动删除。

只有在明确确认内容过时、重复或错误时，才允许人工调整。

## System

`_System` 是机器工作区。

允许存放：

- 插件中间文件
- AnyContent 原始输出
- 插件附件
- 自动化日志
- 临时处理文件

`_System/AnyContent/raw` 可以保留一段时间，用于不重新转录的 Source 重建。

`_System/AnyContent/inbox/_done` 可以在确认 Source 已成功生成后清理。

如果不确定某个 `_System` 文件是否仍有用，先保留，不自动删除。

## Safe Delete Rule

任何自动化清理都必须先输出待删除列表。

没有用户确认，不执行删除。
