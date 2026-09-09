import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from evals.config import load_config
from evals.models.benchmark_client import BenchmarkClient
from evals.reporting.report_generator import generate_report
from evals.runners.extraction_runner import run_extraction
from evals.runners.recommendation_runner import run_recommendation

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = PROJECT_ROOT / "evals"
DEFAULT_CONFIG_PATH = EVALS_DIR / "config.yaml"
DEFAULT_EXTRACTION_DATASET = EVALS_DIR / "datasets" / "extraction_cases.json"
DEFAULT_RECOMMENDATION_DATASET = EVALS_DIR / "datasets" / "recommendation_cases.json"
RESULTS_DIR = EVALS_DIR / "results"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Job Market Analyzer LLM benchmarks.")
    parser.add_argument(
        "command",
        choices=["extraction", "recommendation", "all", "report"],
        help="Benchmark command to run.",
    )
    parser.add_argument(
        "run_directory",
        nargs="?",
        help="Existing run directory for the report command.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to evals config YAML.",
    )
    parser.add_argument(
        "--extraction-dataset",
        type=Path,
        default=DEFAULT_EXTRACTION_DATASET,
        help="Path to extraction dataset JSON.",
    )
    parser.add_argument(
        "--recommendation-dataset",
        type=Path,
        default=DEFAULT_RECOMMENDATION_DATASET,
        help="Path to recommendation dataset JSON.",
    )

    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    config = load_config(args.config)

    if args.command == "report":
        if not args.run_directory:
            parser.error("report requires an existing run directory")

        run_dir = Path(args.run_directory)
        generate_report(run_dir=run_dir, config=config)
        print(f"Report regenerated in: {run_dir}")
        return

    run_id = _run_id()
    run_dir = RESULTS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    metadata = _metadata(run_id, args.command, config)
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    client = BenchmarkClient()

    if args.command in ("extraction", "all"):
        run_extraction(
            config=config,
            client=client,
            run_dir=run_dir,
            run_id=run_id,
            dataset_path=args.extraction_dataset,
        )

    if args.command in ("recommendation", "all"):
        run_recommendation(
            config=config,
            client=client,
            run_dir=run_dir,
            run_id=run_id,
            dataset_path=args.recommendation_dataset,
        )

    generate_report(run_dir=run_dir, config=config, run_metadata=metadata)

    print("")
    print(f"Run saved to: {run_dir}")
    print(f"Models tested: {len(config.enabled_models)}")
    print(f"Runs per case: {config.runs_per_case}")


def _run_id() -> str:
    return datetime.now(tz=UTC).strftime("%Y-%m-%d_%H%M%S")


def _metadata(run_id: str, command: str, config) -> dict[str, object]:
    return {
        "run_id": run_id,
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "benchmark_version": config.benchmark_version,
        "command": command,
        "runs_per_case": config.runs_per_case,
        "extraction_temperature": config.extraction_temperature,
        "extraction_max_tokens": config.extraction_max_tokens,
        "required_skills_weight": config.required_skills_weight,
        "preferred_skills_weight": config.preferred_skills_weight,
        "recommendation_temperature": config.recommendation_temperature,
        "recommendation_max_tokens": config.recommendation_max_tokens,
        "models": [
            {
                "name": model.name,
                "provider": model.provider,
                "model": model.model,
            }
            for model in config.enabled_models
        ],
    }


if __name__ == "__main__":
    main()
