"""
pulls the code out of each response: the first ```python block, falling back to the whole text. It records whether extraction failed.
"""

import re
import ast

code_pattern = re.compile(
    r"```(?:python|py)?[^\n]*\n(.*?)```", re.DOTALL | re.IGNORECASE
)


def extract_code_from_response(response: str):
    response = response.strip()
    match = code_pattern.search(response)
    if match:
        code_block = match.group(1).strip()
    else:
        code_block = response
    try:
        ast.parse(code_block)
        return code_block, False
    except SyntaxError:
        return code_block, True
