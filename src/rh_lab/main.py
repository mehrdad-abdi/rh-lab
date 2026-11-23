from rh_lab.helpers.data import load_mbpp_plus
from rh_lab.helpers.generate import generate_samples_for_tasks
from rh_lab.helpers.sandbox import run_in_docker
import os


MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
SAMPLE_N = 10


def main():
    tasks = load_mbpp_plus()
    print(f"Loaded {len(tasks)} tasks from MBPP+ dataset.")
    os.makedirs("output/raw_completions/", exist_ok=True)

    samples = generate_samples_for_tasks(
        tasks,
        save_path="output/raw_completions/",
        model_name=MODEL,
        n=SAMPLE_N,
        temperature=0.8,
        top_p=0.95,
        max_tokens=512,
        seed=0,
    )

    for task, result in zip(tasks, samples):
        print(f"Grading task {task['task_id']} with generated samples from {result}.")
        run_in_docker(
            "src/rh_lab/helpers/grader.py",
            ["--task", task["task_id"], "--jsonl", result],
        )

    # breakpoint()  # You can inspect the `samples` variable here to see the generated samples for each task.


if __name__ == "__main__":
    main()
