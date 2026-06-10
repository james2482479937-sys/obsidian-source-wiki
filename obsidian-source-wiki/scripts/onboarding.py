"""
Obsidian Source Wiki — First-time onboarding.

What this script automates:
  - vault folder structure creation
  - rule files installation
  - uv installation (Windows: irm installer / Mac+Linux: curl installer)
  - ffmpeg installation (winget on Windows, brew on Mac)
  - Python package `requests` installation
  - anycontent-obsidian-backend repo clone
  - SiliconFlow API key write-in to AnyContent plugin settings
  - final environment check

What still requires manual action (printed at the end):
  - Install Obsidian desktop app
  - Enable Community plugins in Obsidian
  - Install AnyContent Vault Importer from Community plugins
  - Open the vault in Obsidian once (so plugin folder is created)

Usage (agent-driven, all answers from user Q&A):
  python onboarding.py --vault "<path>" --api-key "<sk-xxx>"

Usage (interactive, user answers prompts):
  python onboarding.py
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


# ── helpers ──────────────────────────────────────────────────────────────────

def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, **kwargs)


def run_silent(cmd: list[str]) -> bool:
    try:
        result = run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def which(name: str) -> bool:
    return shutil.which(name) is not None


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        answer = ""
    return answer if answer else default


def section(title: str) -> None:
    print(f"\n── {title} {'─' * max(0, 50 - len(title))}")


def ok(msg: str) -> None:
    print(f"  ✓  {msg}")


def warn(msg: str) -> None:
    print(f"  !  {msg}")


def info(msg: str) -> None:
    print(f"     {msg}")


# ── OS helpers ────────────────────────────────────────────────────────────────

IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"


def install_uv() -> bool:
    """Install uv using the official installer."""
    if IS_WINDOWS:
        cmd = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-Command", "irm https://astral.sh/uv/install.ps1 | iex",
        ]
    else:
        cmd = ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"]
    print("     Installing uv ...")
    result = run(cmd)
    # rehash PATH
    if not which("uv"):
        # try adding ~/.cargo/bin (uv installs there)
        cargo_bin = Path.home() / ".cargo" / "bin"
        os.environ["PATH"] = str(cargo_bin) + os.pathsep + os.environ.get("PATH", "")
    return which("uv")


def install_ffmpeg() -> bool:
    """Install ffmpeg via winget (Windows) or brew (Mac)."""
    if IS_WINDOWS:
        if which("winget"):
            print("     Installing ffmpeg via winget ...")
            result = run(["winget", "install", "--id", "Gyan.FFmpeg", "-e", "--silent"])
            return result.returncode == 0
        else:
            return False
    elif IS_MAC:
        if which("brew"):
            print("     Installing ffmpeg via brew ...")
            result = run(["brew", "install", "ffmpeg"])
            return result.returncode == 0
        else:
            return False
    return False


def install_requests() -> bool:
    python = sys.executable
    result = run([python, "-m", "pip", "install", "--quiet", "requests"])
    return result.returncode == 0


# ── vault detection ───────────────────────────────────────────────────────────

def detect_vault() -> str:
    """Try common Obsidian vault locations."""
    candidates = []
    home = Path.home()
    if IS_WINDOWS:
        candidates = [
            home / "Documents" / "Obsidian",
            home / "iCloudDrive" / "iCloud~md~obsidian",
            home / "OneDrive" / "Obsidian",
        ]
    elif IS_MAC:
        candidates = [
            home / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents",
            home / "Documents" / "Obsidian",
            home / "Obsidian",
        ]
    for c in candidates:
        if c.exists():
            # return the first subfolder that looks like a vault
            for sub in sorted(c.iterdir()):
                if sub.is_dir() and not sub.name.startswith("."):
                    return str(sub)
            return str(c)
    return ""


# ── backend ───────────────────────────────────────────────────────────────────

BACKEND_REPO = "https://github.com/anycontent/anycontent-obsidian-backend.git"
DEFAULT_BACKEND_DIR = Path.home() / "Documents" / "anycontent-obsidian-backend"


def ensure_backend(backend_dir: Path) -> bool:
    if (backend_dir / "web" / "app.py").exists():
        return True
    if not which("git"):
        return False
    print(f"     Cloning AnyContent backend to {backend_dir} ...")
    result = run(["git", "clone", BACKEND_REPO, str(backend_dir)])
    return result.returncode == 0


# ── API key write-in ──────────────────────────────────────────────────────────

def write_api_key(vault: Path, api_key: str) -> str:
    """Write API key into AnyContent plugin data.json if the plugin is installed."""
    plugin_data = vault / ".obsidian" / "plugins" / "anycontent-vault-importer" / "data.json"
    if not plugin_data.exists():
        return "plugin_not_installed"
    try:
        data = json.loads(plugin_data.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    if data.get("apiKey") == api_key:
        return "already_set"
    data["apiKey"] = api_key
    plugin_data.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return "written"


# ── setup_vault helper ────────────────────────────────────────────────────────

def run_setup_vault(vault: Path) -> bool:
    script = Path(__file__).parent / "setup_vault.py"
    result = run([sys.executable, str(script), "--vault", str(vault), "--configure-plugins"])
    return result.returncode == 0


def run_check_environment(vault: Path) -> None:
    script = Path(__file__).parent / "check_environment.py"
    run([sys.executable, str(script), "--vault", str(vault)])


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="First-time onboarding for Obsidian Source Wiki."
    )
    parser.add_argument("--vault", help="Path to the Obsidian vault.")
    parser.add_argument("--api-key", help="SiliconFlow API key (sk-...).")
    parser.add_argument(
        "--backend-dir",
        help="Path to clone/find anycontent-obsidian-backend.",
        default=str(DEFAULT_BACKEND_DIR),
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip system package installation (useful for testing).",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Obsidian Source Wiki — Onboarding")
    print("=" * 60)

    # ── Step 1: Collect answers ──────────────────────────────────
    section("1 / 5  Vault path")
    suggested = detect_vault()
    vault_str = args.vault or ask("Where is your Obsidian vault?", suggested)
    if not vault_str:
        print("ERROR: vault path is required.")
        sys.exit(1)
    vault = Path(vault_str).expanduser().resolve()
    info(f"vault = {vault}")

    section("2 / 5  SiliconFlow API key")
    info("Used for speech-to-text and image OCR.")
    info("Get a free key at https://siliconflow.cn → API Keys")
    api_key = args.api_key or ask("Paste your SiliconFlow API key (sk-...)", "")
    if not api_key:
        warn("No API key provided. Douyin and Xiaohongshu import will not work until you add one.")
        warn("You can re-run this script later with --api-key <your-key>.")

    backend_dir = Path(args.backend_dir).expanduser().resolve()

    # ── Step 2: System dependencies ──────────────────────────────
    section("3 / 5  System dependencies")

    if args.skip_install:
        info("--skip-install: skipping system package installation.")
    else:
        # uv
        if which("uv"):
            ok("uv already installed.")
        else:
            warn("uv not found. Installing ...")
            if install_uv():
                ok("uv installed.")
            else:
                warn("Could not install uv automatically.")
                if IS_WINDOWS:
                    info("Manual: open PowerShell and run:  irm https://astral.sh/uv/install.ps1 | iex")
                else:
                    info("Manual: curl -LsSf https://astral.sh/uv/install.sh | sh")

        # ffmpeg
        if which("ffmpeg"):
            ok("ffmpeg already installed.")
        else:
            warn("ffmpeg not found. Installing ...")
            if install_ffmpeg():
                ok("ffmpeg installed.")
            else:
                warn("Could not install ffmpeg automatically.")
                if IS_WINDOWS:
                    info("Manual: winget install --id Gyan.FFmpeg -e  OR  https://ffmpeg.org/download.html")
                elif IS_MAC:
                    info("Manual: brew install ffmpeg  (requires Homebrew: https://brew.sh)")

        # requests
        try:
            import importlib.util
            if importlib.util.find_spec("requests"):
                ok("Python package 'requests' already installed.")
            else:
                raise ImportError
        except ImportError:
            warn("Python package 'requests' not found. Installing ...")
            if install_requests():
                ok("requests installed.")
            else:
                warn("Could not install requests. Run:  pip install requests")

    # ── Step 3: AnyContent backend ────────────────────────────────
    section("4 / 5  AnyContent backend")
    if (backend_dir / "web" / "app.py").exists():
        ok(f"Backend repo found at {backend_dir}")
    else:
        warn(f"Backend not found at {backend_dir}. Cloning ...")
        if ensure_backend(backend_dir):
            ok(f"Backend cloned to {backend_dir}")
        else:
            warn("Could not clone backend automatically.")
            info(f"Manual: git clone {BACKEND_REPO} {backend_dir}")

    # ── Step 4: Vault setup + API key ─────────────────────────────
    section("5 / 5  Vault setup")
    vault.mkdir(parents=True, exist_ok=True)
    if run_setup_vault(vault):
        ok("Vault folders and rules installed.")
    else:
        warn("setup_vault.py reported an issue. Check output above.")

    if api_key:
        result = write_api_key(vault, api_key)
        if result == "written":
            ok("API key written to AnyContent plugin settings.")
        elif result == "already_set":
            ok("API key already set in AnyContent plugin settings.")
        else:
            warn("AnyContent plugin not installed yet — API key not written.")
            info("After installing the plugin in Obsidian, re-run this script to write the key.")

    # ── Final check ───────────────────────────────────────────────
    section("Environment check")
    run_check_environment(vault)

    # ── Manual steps ──────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  Manual steps remaining (requires Obsidian GUI)")
    print("=" * 60)
    print()
    print("  1. Install Obsidian desktop app if not already installed.")
    print("     https://obsidian.md/download")
    print()
    print("  2. Open Obsidian and add this vault:")
    print(f"     {vault}")
    print()
    print("  3. In Obsidian: Settings → Community plugins → Browse")
    print('     Search "AnyContent Vault Importer" → Install → Enable')
    print()
    print("  4. In Obsidian: AnyContent Vault Importer settings → enter API key:")
    if api_key:
        print(f"     {api_key[:8]}{'*' * (len(api_key) - 8)}")
    else:
        print("     (your SiliconFlow API key)")
    print()
    print("  5. Re-run this script once to confirm everything is ready:")
    print(f"     python onboarding.py --vault \"{vault}\" --api-key <your-key>")
    print()
    print("  Once Obsidian and the plugin are set up, you're ready.")
    print('  Paste any Douyin or Xiaohongshu link into a note under')
    print(f"  {vault / '00_Capture' / 'External'}")
    print("  Then ask the agent: 处理今天的链接")
    print()


if __name__ == "__main__":
    main()
