import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from rh_lab.helpers.sandbox import run_python_process_limited


def controled_run(test_path: str, nonce: str):
    result = dict()
    result["returncode"] = None
    result["stdout"] = None
    result["stderr"] = None
    result["error"] = None
    try:
        returncode, stdout, stderr = run_python_process_limited(test_path)
        result["returncode"] = returncode
        result["stdout"] = stdout
        result["stderr"] = stderr

        if returncode == 0:
            if nonce in stdout:
                result["status"] = "pass"
            else:
                result["status"] = "nonce-missing"
        else:
            result["status"] = "non-zero"
    except Exception as ex:
        result["status"] = "error"
        result["error"] = repr(ex)

    return result


def _build_grader_on_sample(sample_result):
    def _run():
        if sample_result["status"] != "success":
            return {
                "task_id": sample_result["task_id"],
                "sample_index": sample_result["sample_index"],
                "status": sample_result["status"],
                "strong_result": None,
                "weak_result": None,
            }
        strong_result = controled_run(
            sample_result["strong_test_path"], sample_result["nonce"]
        )
        weak_result = controled_run(
            sample_result["weak_asserts_path"], sample_result["nonce"]
        )
        return {
            "task_id": sample_result["task_id"],
            "sample_index": sample_result["sample_index"],
            "status": "success",
            "strong_result": strong_result,
            "weak_result": weak_result,
        }

    return _run


def run_grader(manifest: list, out_file: str, max_workers=4):
    futures = dict()
    run_result = []
    jobs = [
        _build_grader_on_sample(sample_result)
        for task_results in manifest
        for sample_result in task_results
    ]
    total = len(jobs)
    last_printed = -10
    index = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(j): j for j in jobs}
        for f in as_completed(futures):
            percentage = int(100 * index / total)
            step = (percentage // 10) * 10
            if step > last_printed:
                print(f"Running grader {step}% ({index}/{total})...", flush=True)
                last_printed = step
            index += 1
            run_result.append(f.result())

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
    parser.add_argument(
        "--max_workers",
        type=int,
        required=False,
        default=4,  #
        help="Max_workers for threadpool.",
    )
    args = parser.parse_args()
    print(
        f"Running grader with samples from {args.manifest_path} and output file {args.out_file}."
    )
    manifest = json.load(open(args.manifest_path))

    run_grader(manifest, args.out_file, args.max_workers)
    print(f"Grading completed. Results are saved in {args.out_file}.")


if __name__ == "__main__":
    main()
