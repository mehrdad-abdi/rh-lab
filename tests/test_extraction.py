"tests completion extraction from llm responses"

import os

import pytest
import json
from helpers.extract import extract_code_from_response

@pytest.fixture
def completion_success():
    return [
        """```python
def add(a, b):
    # normal case
    return a + b
```""",
        """Here's the solution:
```python
def subtract(a, b):
    # text before the code block
    return a - b
```""",
        """```python
def subtract(a, b):
    # text after the code block
    return a - b
```\nEasy!""",
        """```Python
def subtract(a, b):
    # capital P in Python block
    return a - b
```""",
        """\n\n```Python
def subtract(a, b):
    # whitespace before or after the code block
    return a - b
```\n""",
        """```py
def subtract(a, b):
    # py block 
    return a - b
```""",
        """```
def subtract(a, b):
    # raw code block 
    return a - b
```""",
        """def subtract(a, b):
    # No code block
    return a - b""",
    ]


@pytest.fixture
def completion_failure():
    return [
        "I couldn't find a valid response.",
        "Can you provide more details?",
        "def invalid_formatting(a, b):\n    return a - b```\n\nThis is not a valid code block.",
        "```def invalid_formatting(a, b):\n    return a - b end of code block is missing",
    ]


def test_extract_success(completion_success):
    for completion in completion_success:
        code, extraction_failed = extract_code_from_response(completion)
        assert not extraction_failed, f"Extraction should not fail for a valid response: {completion}"
        assert code.strip().startswith("def "), "Extracted code should start with 'def '."


def test_extract_failure(completion_failure):
    for completion in completion_failure:
        code, extraction_failed = extract_code_from_response(completion)
        assert extraction_failed, f"Extraction should fail for an invalid response: {completion}"
        assert code == completion, "Extracted code should be the same as the original response when extraction fails."

def test_output_raw():
    if not os.path.exists("output/raw_completions/"):
        pytest.skip("Raw completions directory does not exist. Run step_1.py to generate samples.")

    for filename in os.listdir("output/raw_completions/"):
        if filename.endswith(".jsonl"):
            with open(os.path.join("output/raw_completions/", filename), "r") as f:
                line_no = 0
                for line in f:
                    data = json.loads(line.strip())
                    assert "raw_response" in data, "Each line should contain a 'raw_response' field."
                    code, extraction_status = extract_code_from_response(data["raw_response"])
                    if not extraction_status:
                        print(f"check extraction for {filename}: {line_no}...")
                    line_no += 1