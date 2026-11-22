"""
builds the chat messages for a task. One system message ("return only one Python code block") and one user message
"""


def _extract_function_name(task):
    # Extract the function name from the task prompt
    lines = task["code"].splitlines()
    for line in lines:
        if line.startswith("def "):
            return line.split("(")[0][4:]  # Extract function name

    raise ValueError("Function definition not found in the task code.")


def _extract_example(task):
    return "\n".join(task["test_list"])


def build_chat_messages(task):
    messages = [
        {
            "role": "system",
            "content": "You are a Python programmer. Reply with a single Python code block "
            "containing the complete solution. Do not include explanations.",
        },
        {
            "role": "user",
            "content": task["prompt"]
            + "\n\n"
            + f"The function must be named `{_extract_function_name(task)}`.\n\n"
            "Examples:\n"
            "```python\n"
            f"{_extract_example(task)}\n"
            "```",
        },
    ]
    return messages
