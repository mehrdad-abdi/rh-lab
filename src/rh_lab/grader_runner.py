import argparse
import json
import os
from rh_lab.helpers.sandbox import run_python_process_limited


def run_grader(manifest: list, out_file: str):
    run_result = []
    total = len(manifest)
    last_printed = -10

    for index, task_results in enumerate(manifest):
        percentage = int(100 * index / total)
        step = (percentage // 10) * 10
        if step > last_printed:
            print(f"Running grader ({index}/{total})...", flush=True)
            last_printed = step
        result_for_task = {}
        for sample_result in task_results:
            if sample_result["status"] != "success":
                result_for_task = {
                    "task_id": sample_result["task_id"],
                    "sample_index": sample_result["sample_index"],
                    "status": sample_result["status"],
                }

                continue  # Skip samples that failed to build graders

            # Run the grader for this sample
            solution_path = sample_result["solution_path"]
            weak_asserts_path = sample_result["weak_asserts_path"]
            strong_test_path = sample_result["strong_test_path"]

            # Run the grader in a sandboxed environment
            returncode, stdout, stderr = run_python_process_limited(strong_test_path)
            result_for_task = {
                "task_id": sample_result["task_id"],
                "sample_index": sample_result["sample_index"],
                "status": "success",
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode,
            }

            # Run the grader in a sandboxed environment
            returncode, stdout, stderr = run_python_process_limited(weak_asserts_path)
            result_for_task = {
                "task_id": sample_result["task_id"],
                "sample_index": sample_result["sample_index"],
                "status": "success",
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode,
            }

        run_result.append(result_for_task)

    with open(out_file, "w") as f:
        json.dump(run_result, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Run the grader.")
    parser.add_argument(
        "--manifest_path",
        type=str,
        required=True,
        help="Path to the manifest file.",
    )
    parser.add_argument(
        "--out_file",
        type=str,
        required=True,
        help="Path to the output file.",
    )
    args = parser.parse_args()
    print(
        f"Running grader with samples from {args.manifest_path} and output file {args.out_file}."
    )
    manifest = json.load(open(args.manifest_path))

    run_grader(manifest, args.out_file)
    print(f"Grading completed. Results are saved in {args.out_file}.")


if __name__ == "__main__":
    main()
