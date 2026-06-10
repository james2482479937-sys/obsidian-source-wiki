import argparse
import shutil
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

        structured_source = vault / "10_Sources" / "2026-06-10" / "structured-source.md"
        write(
            structured_source,
            """---
title: "structured-source"
created: 2026-06-10
status: source_structured
knowledge_links: []
---

# structured-source

## Source Info

- 原链接：https://example.com

## 第一个主题：背景和问题

这里是一段结构化后的源材料，保留原始内容的意思，并且把自然段切开。

## 第二个主题：具体例子

这里记录来源中提到的例子，不做过度总结。

## 第三个主题：结论和后续

这里记录来源最后收束到的判断，方便以后回溯阅读。

## Structure Tags

- 主题：测试
- 人物：
- 概念：
- 场景：

## Linked Knowledge

- 
""",
        )
        run(
            [
                sys.executable,
                str(skill / "scripts" / "validate_source_structure.py"),
                "--source",
                str(structured_source),
            ],
            cwd=skill,
        )

        capture = vault / "00_Capture" / "External" / "2026-06-10" / "links.md"
        write(
            capture,
            "小红书测试 http://xhslink.com/o/example\n抖音测试 https://v.douyin.com/example/ 保存图片\n",
        )
        dry_run = run(
            [
                sys.executable,
                str(skill / "scripts" / "process_capture_links.py"),
                "--vault",
                str(vault),
                "--capture-file",
                str(capture),
                "--dry-run",
            ],
            cwd=skill,
        )
        assert "xhs" in dry_run
        assert "anycontent" in dry_run
        assert "save_images" in dry_run

        if args.keep:
            keep_path = Path.cwd() / "_smoke_test_vault"
            if keep_path.exists():
                shutil.rmtree(keep_path)
            shutil.copytree(vault, keep_path)
            print(f"kept={keep_path}")

    print("smoke_test=ok")


if __name__ == "__main__":
    main()
