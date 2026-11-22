from helpers.data import load_mbpp_plus
from helpers.generate import generate_samples_for_tasks
import os


MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
SAMPLE_N = 10

if __name__ == "__main__":
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

    # breakpoint()  # You can inspect the `samples` variable here to see the generated samples for each task.
