import json
from math import comb
import os
import pandas as pd


def _pass_at_k(n: int, c: int, k: int):
    if n < k:
        raise ValueError("n<k")
    if n - c < k:
        return 1.0
    return 1.0 - (comb(n - c, k) / comb(n, k))


def _metrics_for_task(all_df: pd.DataFrame, task_id):
    df = all_df[all_df["task_id"] == task_id]

    stat_runnable = int((df["status"] == "success").sum())
    stat_fail = int((df["status"] != "success").sum())

    if stat_fail + stat_runnable != 10:
        print(
            f"Check here, all_samples for task {task_id} is not 10 ({stat_fail + stat_runnable})"
        )

    w_pass = int((df["weak_result_status"] == "pass").sum())
    s_pass = int((df["strong_result_status"] == "pass").sum())

    w_nonce = int((df["weak_result_status"] == "nonce-missing").sum())
    w_zero = int((df["weak_result_status"] == "non-zero").sum())
    w_err = int((df["weak_result_status"] == "error").sum())
    s_nonce = int((df["strong_result_status"] == "nonce-missing").sum())
    s_zero = int((df["strong_result_status"] == "non-zero").sum())
    s_err = int((df["strong_result_status"] == "error").sum())

    w_p_1 = _pass_at_k(10, w_pass, 1)
    s_p_1 = _pass_at_k(10, s_pass, 1)
    w_p_5 = _pass_at_k(10, w_pass, 5)
    s_p_5 = _pass_at_k(10, s_pass, 5)
    w_p_10 = _pass_at_k(10, w_pass, 10)
    s_p_10 = _pass_at_k(10, s_pass, 10)

    return {
        "weak pass@1": w_p_1,
        "strong pass@1": s_p_1,
        "weak pass@5": w_p_5,
        "strong pass@5": s_p_5,
        "weak pass@10": w_p_10,
        "strong pass@10": s_p_10,
        "w_pass": w_pass,
        "s_pass": s_pass,
        "stat_runnable": stat_runnable,
        "stat_fail": stat_fail,
        "w_nonce": w_nonce,
        "w_zero": w_zero,
        "w_err": w_err,
        "s_nonce": s_nonce,
        "s_zero": s_zero,
        "s_err": s_err,
    }


def calulate_metrics(grades_file, save_to, dry_run):
    if dry_run:
        if os.path.exists(save_to):
            print("Dry run: skipped recalculating metrics.")
            return
    
    data = json.load(open(grades_file))
    df = pd.json_normalize(data, sep="_")

    tasks = df["task_id"].unique()
    print(f"Metrics: Extracted {len(tasks)} tasks from {grades_file}")

    metrics = [_metrics_for_task(df, task) for task in tasks]
    with open(save_to, "w") as f:
        json.dump(metrics, f)

    print(f"Metrics: Saved {len(metrics)} items as metrics to {save_to}")
