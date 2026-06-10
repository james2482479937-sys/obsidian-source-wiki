# Quick Start

从零到"丢一个链接，agent 自动处理成 Source"，约 10 分钟。

---

## 前置条件（只需手动做一次）

**1. 安装 Obsidian 桌面端**

https://obsidian.md/download

**2. 安装 AnyContent Vault Importer 插件**

打开 Obsidian → Settings → Community plugins → Browse  
搜索 `AnyContent Vault Importer` → Install → Enable

**3. 准备一个 SiliconFlow API key**

注册并获取免费 key：https://siliconflow.cn → API Keys  
（用于视频语音转文字和图片 OCR）

---

## 一条命令完成剩余所有配置

确保已安装 Python 3.10+，然后：

```bash
python obsidian-source-wiki/scripts/onboarding.py
```

脚本会问你两个问题：

1. **你的 Obsidian vault 在哪里？**（通常可以直接回车用自动检测到的路径）
2. **你的 SiliconFlow API key 是？**（粘贴进去）

然后脚本自动完成：

- ✅ 安装 `uv`（用于启动 AnyContent 后端）
- ✅ 安装 `ffmpeg`（用于小红书视频处理）
- ✅ 安装 Python 包 `requests`
- ✅ 克隆 AnyContent 后端到本地
- ✅ 创建 vault 文件夹结构
- ✅ 写入 API key 到插件配置
- ✅ 运行环境检查，输出 `environment_ready=true`

---

## 开始使用

1. 打开 Obsidian，确认 vault 已加载
2. 在 `00_Capture/External/` 下新建一个笔记，粘贴任意抖音或小红书链接
3. 打开 Claude Code，对 agent 说：

```
处理今天的链接
```

agent 会自动：读取链接 → 下载视频/图文 → 转录 → 生成结构化 Source → 校验

---

## 如果遇到问题

```bash
python obsidian-source-wiki/scripts/check_environment.py --vault "<你的vault路径>"
```

输出会明确告诉你哪一步还缺什么。

详细故障排查：`obsidian-source-wiki/references/troubleshooting.md`
