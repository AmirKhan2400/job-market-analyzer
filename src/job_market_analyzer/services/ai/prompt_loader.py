from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = PACKAGE_ROOT / "prompts"


def load_prompt(filename: str) -> str:
    prompt_path = PROMPTS_DIR / filename

    with prompt_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        return file.read()
