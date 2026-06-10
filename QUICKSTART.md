# Quick Start

从零到"丢一个链接，agent 自动处理成 Source"，约 10 分钟。

---

## 第一步：安装 Obsidian（让 agent 帮你执行）

**Windows（让 agent 在终端运行）：**
```powershell
winget install Obsidian.Obsidian
```

**Mac（让 agent 在终端运行）：**
```bash
brew install --cask obsidian
```

或直接下载：https://obsidian.md/download

---

## 第二步：准备 SiliconFlow API key

注册并获取免费 key：https://siliconflow.cn → API Keys  
（用于视频语音转文字和图片 OCR，免费额度足够日常使用）

---

## 第三步：运行 onboarding 脚本（让 agent 帮你执行）

确保已安装 Python 3.10+，让 agent 运行：

```bash
python obsidian-source-wiki/scripts/onboarding.py
```

脚本会问你两个问题：

1. **你的 Obsidian vault 在哪里？**（通常可以直接回车用自动检测到的路径）
2. **你的 SiliconFlow API key 是？**（粘贴进去）

然后 agent 帮你自动完成：

- ✅ 安装 `uv`（用于启动 AnyContent 后端）
- ✅ 安装 `ffmpeg`（用于小红书视频处理）
- ✅ 安装 Python 包 `requests`
- ✅ 克隆 AnyContent 后端到本地
- ✅ 创建 vault 文件夹结构
- ✅ 写入 API key 到插件配置
- ✅ 运行环境检查

---

## 第四步：安装 AnyContent Vault Importer 插件

打开 Obsidian → Settings → Community plugins → 打开 Community plugins → Browse  
搜索 `AnyContent Vault Importer` → Install → Enable

完成后让 agent 再跑一次 onboarding，它会自动把 API key 写入插件配置：

```bash
python obsidian-source-wiki/scripts/onboarding.py --vault "<你的vault路径>" --api-key "<你的key>"
```

最终看到 `environment_ready=true` 即表示配置完成。

---

## 开始使用

1. 打开 Obsidian，确认 vault 已加载
2. 在 `00_Capture/External/` 下新建一个笔记，粘贴任意抖音或小红书链接
3. 对 agent 说：

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
