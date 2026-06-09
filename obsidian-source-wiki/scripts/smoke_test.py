import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def run(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(command)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result.stdout


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a no-network smoke test for obsidian-source-wiki.")
    parser.add_argument("--keep", action="store_true", help="Keep the temporary vault for inspection.")
    args = parser.parse_args()

    skill = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="obsidian-source-wiki-") as temp:
        vault = Path(temp) / "TestVault"
        run([sys.executable, str(skill / "scripts" / "setup_vault.py"), "--vault", str(vault)], cwd=skill)
        env_output = run([sys.executable, str(skill / "scripts" / "check_environment.py"), "--vault", str(vault)], cwd=skill)
        if "missing_requirements:" not in env_output:
            raise RuntimeError("Environment check should report missing requirements for a fresh vault.")

        source = vault / "10_Sources" / "2026-06-10" / "test-source.md"
        write(
            source,
            """---
title: "test-source"
created: 2026-06-10
knowledge_links: []
---

# test-source

## Linked Knowledge

- 
""",
        )
        run(
            [
                sys.executable,
                str(skill / "scripts" / "create_knowledge_note.py"),
                "--vault",
                str(vault),
                "--source",
                str(source),
                "--type",
                "Concepts",
                "--title",
                "test-concept",
            ],
            cwd=skill,
        )
        source_text = source.read_text(encoding="utf-8")
        knowledge = vault / "20_Knowledge" / "Concepts" / "test-concept.md"
        knowledge_text = knowledge.read_text(encoding="utf-8")
        assert "[[20_Knowledge/Concepts/test-concept]]" in source_text
        assert "[[10_Sources/2026-06-10/test-source]]" in knowledge_text

        if args.keep:
            keep_path = Path.cwd() / "_smoke_test_vault"
            if keep_path.exists():
                import shutil

                shutil.rmtree(keep_path)
            import shutil

            shutil.copytree(vault, keep_path)
            print(f"kept={keep_path}")

    print("smoke_test=ok")


if __name__ == "__main__":
    main()
