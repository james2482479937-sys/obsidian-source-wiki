import argparse
import json
import shutil
from pathlib import Path


FOLDERS = [
    "00_Capture/External",
    "00_Capture/Personal",
    "10_Sources",
    "20_Knowledge/Concepts",
    "20_Knowledge/Methods",
    "20_Knowledge/Projects",
    "20_Knowledge/Workflows",
    "20_Knowledge/Media",
    "90_Rules/Templates",
    "_System/AnyContent/inbox",
    "_System/AnyContent/raw",
    "_System/AnyContent/media",
    "_System/Attachments",
    "_System/Plugin_Output/XHS",
    "_System/Logs",
]


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def copy_rules(vault: Path, overwrite: bool) -> None:
    src = skill_root() / "assets" / "rules"
    dst = vault / "90_Rules"
    dst.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        return
    for path in src.glob("*.md"):
        target = dst / path.name
        if target.exists() and not overwrite:
            continue
        shutil.copy2(path, target)


def patch_plugin_json(path: Path, updates: dict) -> bool:
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    changed = False
    for key, value in updates.items():
        if data.get(key) != value:
            data[key] = value
            changed = True
    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return changed


def configure_plugins(vault: Path) -> list[str]:
    messages = []
    obsidian = vault / ".obsidian" / "plugins"
    anycontent = obsidian / "anycontent-vault-importer" / "data.json"
    if patch_plugin_json(
        anycontent,
        {
            "rawFolder": "_System/AnyContent/raw",
            "inboxFolder": "_System/AnyContent/inbox",
            "inboxAutoConsume": True,
            "mediaFolder": "media",
            "saveVideoLocally": False,
        },
    ):
        messages.append("updated AnyContent settings")
    elif anycontent.exists():
        messages.append("AnyContent settings already compatible")
    else:
        messages.append("AnyContent plugin settings not found")

    xhs = obsidian / "xhs-importer" / "data.json"
    if patch_plugin_json(
        xhs,
        {
            "noteFolder": "_System/Plugin_Output/XHS",
            "imageFolder": "_System/Attachments/XHS",
            "downloadMedia": False,
        },
    ):
        messages.append("updated XHS Importer settings")
    elif xhs.exists():
        messages.append("XHS Importer settings already compatible")
    else:
        messages.append("XHS Importer plugin settings not found")
    return messages


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize an Obsidian Source Wiki vault.")
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault.")
    parser.add_argument("--overwrite-rules", action="store_true", help="Overwrite existing 90_Rules markdown files.")
    parser.add_argument("--configure-plugins", action="store_true", help="Patch known plugin settings if present.")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    vault.mkdir(parents=True, exist_ok=True)
    for folder in FOLDERS:
        (vault / folder).mkdir(parents=True, exist_ok=True)
    copy_rules(vault, overwrite=args.overwrite_rules)

    print(f"vault={vault}")
    print(f"folders_created={len(FOLDERS)}")
    print("rules_copied=true")
    if args.configure_plugins:
        for message in configure_plugins(vault):
            print(message)
    print("")
    print("next_steps:")
    print("1. Open this vault in Obsidian desktop.")
    print("2. Enable Community plugins.")
    print("3. Install and enable AnyContent Vault Importer.")
    print("4. Start the AnyContent backend at http://127.0.0.1:8080.")
    print("5. Register SiliconFlow and enter its API key in AnyContent settings.")
    print("6. Install ffmpeg if video transcription is needed.")
    print("7. Ensure Python package requests is installed for Xiaohongshu processing.")
    print("8. Run check_environment.py before processing media links.")
    print("")
    print("agent_instruction: After folder creation, report these next steps to the user. Do not claim the media workflow is ready until check_environment.py reports environment_ready=true.")


if __name__ == "__main__":
    main()
