import argparse
import json
import os
from rh_lab.helpers.sandbox import run_python_process_limited


def run_grader(manifest: list, out_dir: str):
    run_result = []
    for task_results in manifest:
        result_for_task = {}
        for sample_result in task_results:
            if sample_result["status"] != "success":
                result_for_task.append(
                    {
                        "task_id": sample_result["task_id"],
                        "sample_index": sample_result["sample_index"],
                        "status": sample_result["status"],
                    }
                )
                continue  # Skip samples that failed to build graders

            # Run the grader for this sample
            solution_path = sample_result["solution_path"]
            weak_asserts_path = sample_result["weak_asserts_path"]
            strong_test_path = sample_result["strong_test_path"]

            # Run the grader in a sandboxed environment
            returncode, stdout, stderr = run_python_process_limited(
                script_path=strong_test_path
            )
            result_for_task.append(
                {
                    "task_id": sample_result["task_id"],
                    "sample_index": sample_result["sample_index"],
                    "status": "success",
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": returncode,
                }
            )

            # Run the grader in a sandboxed environment
            returncode, stdout, stderr = run_python_process_limited(
                script_path=weak_asserts_path
            )
            result_for_task.append(
                {
                    "task_id": sample_result["task_id"],
                    "sample_index": sample_result["sample_index"],
                    "status": "success",
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": returncode,
                }
            )


def main():
    parser = argparse.ArgumentParser(description="Run the grader.")
    parser.add_argument(
        "--manifest_path",
        type=str,
        required=True,
        help="Path to the manifest file.",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        required=True,
        help="Path to the output directory.",
    )
    args = parser.parse_args()
    print(
        f"Running grader with samples from {args.manifest_path} and output directory {args.out_dir}."
    )
    manifest = json.load(open(args.manifest_path))
    os.makedirs(args.out_dir, exist_ok=True)

    run_grader(manifest, args.out_dir)
    print(f"Grading completed. Results are saved in {args.out_dir}.")


if __name__ == "__main__":
    main()
