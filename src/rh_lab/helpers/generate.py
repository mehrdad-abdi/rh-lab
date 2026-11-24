"""
runs vLLM over all tasks with n samples each and writes samples.jsonl (task id, sample index, raw response).
"""

from vllm import LLM, SamplingParams
from .prompts import build_chat_messages
import json
import os
from pathlib import Path


def _return_saved_results(tasks, save_path):
    all_samples = dict()
    for task in tasks:
        file_path = f"{save_path}task_{task['task_id']}.jsonl"
        all_samples[task["task_id"]] = file_path

    print("Dry run; skipped calling LLM and reurned the cached files.")
    return all_samples


def generate_samples_for_tasks(
    tasks,
    model_name: str,
    save_path: str = "output/raw_completions/",
    gpu_memory_utilization: float = 0.85,
    max_model_len: int = 4096,
    n: int = 10,
    temperature: float = 0.8,
    top_p: float = 0.95,
    max_tokens: int = 512,
    seed: int = 0,
    dry_run: bool = False,
):
    if dry_run:
        if os.path.isdir(save_path) and os.listdir(save_path):
            return _return_saved_results(tasks, save_path)
    llm = LLM(
        model=model_name,
        gpu_memory_utilization=gpu_memory_utilization,
        max_model_len=max_model_len,
        seed=seed,
    )
    print(
        f"Loaded model {model_name} with max_model_len={max_model_len} and gpu_memory_utilization={gpu_memory_utilization}."
    )
    params = SamplingParams(
        n=n, temperature=temperature, top_p=top_p, max_tokens=max_tokens, seed=seed
    )
    print(
        f"Sampling parameters: n={n}, temperature={temperature}, top_p={top_p}, max_tokens={max_tokens}, seed={seed}."
    )

    conversations = [build_chat_messages(task) for task in tasks]
    print(f"Built chat messages for {len(conversations)} tasks.")
    outputs = llm.chat(messages=conversations, sampling_params=params)
    print(f"Generated samples for {len(outputs)} tasks.")
    all_samples = dict()
    for task, out in zip(tasks, outputs):
        file_path = f"{save_path}task_{task['task_id']}.jsonl"
        all_samples[task["task_id"]] = file_path
        with open(file_path, "w") as f:
            for completion in out.outputs:
                f.write(json.dumps({"raw_response": completion.text}) + "\n")

    print(f"Finished generating samples for all tasks.")
    return all_samples
