import json
from math import comb
import os
import pandas as pd

METRIC_COLS = [
    "stat_runnable",
    "stat_fail",
    "w_pass",
    "s_pass",
    "w_nonce",
    "w_zero",
    "w_err",
    "s_nonce",
    "s_zero",
    "s_err",
]


def _pass_at_k(n: int, c: int, k: int):
    if n < k:
        raise ValueError("n<k")
    if n - c < k:
        return 1.0
    return 1.0 - (comb(n - c, k) / comb(n, k))


def calulate_metrics(grades_file, save_to, dry_run):
    if dry_run:
        if os.path.exists(save_to):
            print("Dry run: skipped recalculating metrics.")
            return

    data = json.load(open(grades_file))
    df = pd.json_normalize(data, sep="_")

    print(f"Metrics: Extracted {df['task_id'].nunique()} tasks from {grades_file}")

    df["stat_runnable"] = df["status"] == "success"
    df["stat_fail"] = df["status"] != "success"
    df["w_pass"] = df["weak_result_status"] == "pass"
    df["s_pass"] = df["strong_result_status"] == "pass"
    df["w_nonce"] = df["weak_result_status"] == "nonce-missing"
    df["w_zero"] = df["weak_result_status"] == "non-zero"
    df["w_err"] = df["weak_result_status"] == "error"
    df["s_nonce"] = df["strong_result_status"] == "nonce-missing"
    df["s_zero"] = df["strong_result_status"] == "non-zero"
    df["s_err"] = df["strong_result_status"] == "error"

    metrics_df = df.groupby("task_id", sort=False)[METRIC_COLS].sum().reset_index()
    n_samples = metrics_df["stat_runnable"] + metrics_df["stat_fail"]

    for k in (1, 5, 10):
        metrics_df[f"weak pass@{k}"] = [
            _pass_at_k(int(n), int(c), k)
            for n, c in zip(n_samples, metrics_df["w_pass"])
        ]
        metrics_df[f"strong pass@{k}"] = [
            _pass_at_k(int(n), int(c), k)
            for n, c in zip(n_samples, metrics_df["s_pass"])
        ]

    metrics_df.to_json(save_to, orient="records", indent=2)
    metrics_df.to_csv(save_to.replace(".json", ".csv"), encoding="utf-8-sig")

    print(f"Metrics: Saved metrics to {save_to}")
