import argparse
from rh_lab.helpers.data import load_mbpp_plus
from rh_lab.helpers.generate import generate_samples_for_tasks
from rh_lab.helpers.grade import build_graders, run_graders
import os
import json


def lab_process(config, dry_run):
    tasks = load_mbpp_plus()
    print(f"Loaded {len(tasks)} tasks from MBPP+ dataset.")
    os.makedirs(config["save_path"], exist_ok=True)

    samples = generate_samples_for_tasks(
        tasks,
        save_path=config["save_path"],
        model_name=config["model"],
        n=config["sample_n"],
        temperature=config["temperature"],
        top_p=config["top_p"],
        max_tokens=config["max_tokens"],
        seed=config["seed"],
        dry_run=dry_run,
    )

    os.makedirs(config["grader_out_dir"], exist_ok=True)

    build_graders(
        tasks,
        samples,
        config["grader_out_dir"],
        config["manifest_file"],
        dry_run=dry_run,
    )
    run_graders(config["manifest_file"], config["grade_result_dir"])


def main():
    parser = argparse.ArgumentParser(description="Reward-Hacking Lab.")
    parser.add_argument(
        "--config", default="config.json", help="Path to the configuration file."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without generating samples.",
    )
    args = parser.parse_args()

    config = json.load(open(args.config))

    lab_process(config, args.dry_run)


if __name__ == "__main__":
    main()
