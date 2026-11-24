"""
builds two programs per sample (imports + candidate + weak asserts, and imports + candidate + strong test), runs both in the sandbox, and writes results.jsonl.
"""

import json
import os
from .extract import extract_code_from_response
from .sandbox import run_in_docker


def _build_weak_asserts_program(task: dict, save_to: str) -> str:
    with open(save_to, "w") as weak_grade:
        weak_grade.write("from solution import *\n")
        for line in task["test_imports"]:
            weak_grade.write(line + "\n")
        for line in task["test_list"]:
            weak_grade.write(line + "\n")


def _build_strong_test_program(task: dict, save_to: str) -> str:
    with open(save_to, "w") as strong_test:
        strong_test.write("from solution import *\n")
        strong_test.write(task["test"] + "\n")


def _build_solution_program(task: dict, sample: str, save_to: str) -> str:
    raw_response = sample["raw_response"]
    code_block, failed = extract_code_from_response(raw_response)
    if failed:
        print(
            f"Warning: Failed to extract code from response for task {task['task_id']}. Using raw response."
        )
        return False

    with open(save_to, "w") as solution:
        solution.write(code_block + "\n")

    return True


def _build_graders_for_task(task: dict, sample_path: str, out_dir: str):
    results = []
    with open(sample_path, "r") as file:
        for line_num, line in enumerate(file.readlines(), start=1):
            os.makedirs(
                out_dir + f"task_{task['task_id']}/sample_{line_num}/", exist_ok=True
            )
            sample = json.loads(line)
            solution_path = (
                out_dir + f"task_{task['task_id']}/sample_{line_num}/solution.py"
            )
            weak_asserts_path = (
                out_dir + f"task_{task['task_id']}/sample_{line_num}/weak_asserts.py"
            )
            strong_test_path = (
                out_dir + f"task_{task['task_id']}/sample_{line_num}/strong_test.py"
            )

            success = _build_solution_program(task, sample, solution_path)
            if not success:
                results.append(
                    {
                        "task_id": task["task_id"],
                        "sample_index": line_num,
                        "status": "failed_to_extract_code",
                    }
                )
                continue

            _build_weak_asserts_program(task, weak_asserts_path)
            _build_strong_test_program(task, strong_test_path)
            results.append(
                {
                    "task_id": task["task_id"],
                    "sample_index": line_num,
                    "status": "success",
                    "solution_path": solution_path,
                    "weak_asserts_path": weak_asserts_path,
                    "strong_test_path": strong_test_path,
                }
            )

    return results


def build_graders(
    tasks: list,
    samples: dict,
    out_dir: str,
    manifest_save_to: str,
    dry_run: bool = False,
):
    manifest = []
    if dry_run:
        if os.path.exists(manifest_save_to):
            print("Dry run: skipped building graders.")
            return
    for task in tasks:
        sample_path = samples[task["task_id"]]
        manifest.append(_build_graders_for_task(task, sample_path, out_dir))

    with open(manifest_save_to, "w") as f:
        json.dump(manifest, f, indent=4)

    print(
        f"Finished building graders for all tasks. Graders are saved in {out_dir}, manifest saved in {manifest_save_to}."
    )


def run_graders(manifest_path: str, out_dir: str, dry_run: bool = False):
    if dry_run:
        return
    run_in_docker(
        [
            "python",
            "-m",
            "rh_lab.grader_runner",
            "--manifest_path",
            manifest_path,
            "--out_file",
            "/out/grades.json",
        ],
        out_dir=out_dir,
        extra=["-e", "PYTHONPATH=/work/src"],
    )
