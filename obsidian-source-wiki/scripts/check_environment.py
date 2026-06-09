import argparse
import os
import json
import shutil
import socket
import importlib.util
from pathlib import Path


RECOMMENDED_PLUGINS = {
    "anycontent-vault-importer": "required for Douyin/TikTok/WeChat/YouTube import and ASR/OCR API key storage",
    "xhs-importer": "optional helper for Xiaohongshu clipping",
    "mindelixir-mindmap": "optional mind map rendering for structured Markdown",
    "quickadd": "optional capture shortcuts",
    "obsidian-excalidraw-plugin": "optional diagrams and sketches",
}


def has_api_key(vault: Path) -> bool:
    path = vault / ".obsidian" / "plugins" / "anycontent-vault-importer" / "data.json"
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return bool((data.get("apiKey") or "").strip())


def backend_reachable(host: str = "127.0.0.1", port: int = 8080) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def discover_backend_dir() -> Path | None:
    candidates = []
    env_path = os.environ.get("ANYCONTENT_BACKEND_DIR")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend(
        [
            Path.cwd() / "anycontent-obsidian-backend",
            Path.home() / "Documents" / "anycontent-obsidian-backend",
            Path.home() / "anycontent-obsidian-backend",
        ]
    )
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "web" / "app.py").exists():
            return resolved
    return None


def module_exists(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def main() -> None:
    parser = argparse.ArgumentParser(description="Check an Obsidian Source Wiki environment.")
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault.")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    missing = []

    print(f"vault_exists={vault.exists()} {vault}")
    if not vault.exists():
        missing.append("Create or open the Obsidian vault path.")

    plugins_dir = vault / ".obsidian" / "plugins"
    print(f"plugins_dir_exists={plugins_dir.exists()} {plugins_dir}")
    if not plugins_dir.exists():
        missing.append("Open the vault in Obsidian desktop and enable Community plugins.")

    for plugin, reason in RECOMMENDED_PLUGINS.items():
        exists = (plugins_dir / plugin).exists()
        print(f"plugin:{plugin}={'ok' if exists else 'missing'} - {reason}")
        if plugin == "anycontent-vault-importer" and not exists:
            missing.append("Install and enable Obsidian plugin: AnyContent Vault Importer.")

    api_key_ok = has_api_key(vault)
    print(f"anycontent_api_key={'ok' if api_key_ok else 'missing'}")
    if not api_key_ok:
        missing.append("Register SiliconFlow and enter its API key in AnyContent Vault Importer settings.")

    backend_ok = backend_reachable()
    backend_dir = discover_backend_dir()
    uv_ok = bool(shutil.which("uv"))
    backend_startable = bool(backend_dir and uv_ok)
    backend_status = "ok" if backend_ok else "auto_start_available" if backend_startable else "missing"
    print(f"anycontent_backend={backend_status} http://127.0.0.1:8080")
    print(f"anycontent_backend_repo={'ok' if backend_dir else 'missing'} {backend_dir or ''}")
    print(f"uv={'ok' if uv_ok else 'missing'}")
    if not backend_ok and not backend_startable:
        missing.append("Install uv and clone anycontent-obsidian-backend so the unified processor can start the backend.")

    ffmpeg_ok = bool(shutil.which("ffmpeg"))
    python_ok = bool(shutil.which("python"))
    requests_ok = module_exists("requests")
    print(f"ffmpeg={'ok' if ffmpeg_ok else 'missing'}")
    print(f"python={'ok' if python_ok else 'missing'}")
    print(f"python_module:requests={'ok' if requests_ok else 'missing'}")
    if not ffmpeg_ok:
        missing.append("Install ffmpeg for Xiaohongshu video audio extraction.")
    if not python_ok:
        missing.append("Install Python to run the bundled scripts.")
    if not requests_ok:
        missing.append("Install Python package: requests. The Xiaohongshu adapter needs it.")

    system = vault / "_System"
    print(f"system_folder={'ok' if system.exists() else 'missing'} {system}")
    if not system.exists():
        missing.append("Run setup_vault.py to create _System and rule folders.")

    print("")
    if missing:
        print("missing_requirements:")
        for item in missing:
            print(f"- {item}")
        print("")
        print("blocked_until_fixed:")
        print("- Douyin import requires AnyContent plugin, AnyContent backend, and SiliconFlow API key.")
        print("- Xiaohongshu video transcription requires SiliconFlow API key and ffmpeg.")
        print("- Xiaohongshu image OCR requires SiliconFlow API key with OCR/vision balance.")
        print("")
        print("agent_instruction: Report these missing requirements to the user. Do not claim setup is complete.")
    else:
        print("environment_ready=true")
        print("agent_instruction: Media import can be tested with a sample Capture link.")


if __name__ == "__main__":
    main()
