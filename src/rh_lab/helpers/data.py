"""
loads MBPP+ and returns task records: id, description, function name, weak tests, strong test program, imports, reference code
"""

from datasets import load_dataset


def load_mbpp_plus():
    return load_dataset("evalplus/mbppplus", split="test")
