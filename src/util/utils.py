import html
import re
from typing import Dict, List

import markdown
import numpy as np


def normalize(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)


def make_orthogonal(target: np.ndarray, reference: np.ndarray) -> np.ndarray:
    return target - np.inner(target, reference) * reference


def read_md(path: str) -> Dict[str, str]:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'<!--([a-zA-Z0-9]*)-->'
    matches = list(re.finditer(pattern, content))
    result: Dict[str, str] = {}
    for i, match in enumerate(matches):
        label = match.group(1)
        text_start = match.end()
        text_end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        if not label:
            label = str(i)
        result[label] = content[text_start:text_end].strip()
    return result


math_pattern = re.compile(r'\$\$(.+?)\$\$|(?<!\\)\$(.+?)(?<!\\)\$', re.DOTALL)
math_placeholder_pattern = re.compile(r'MATHPLACEHOLDER(\d+)END')


def render_markdown(text: str) -> str:
    # formulas are replaced with placeholders, so that markdown does not mangle underscores and backslashes,
    # and then restored with MathJax delimiters
    formulas: List[str] = []

    def protect(match: re.Match) -> str:
        display, inline = match.groups()
        formula = rf'\[{display}\]' if display is not None else rf'\({inline}\)'
        formulas.append(html.escape(formula, quote=False))
        return f'MATHPLACEHOLDER{len(formulas) - 1}END'

    rendered = markdown.markdown(math_pattern.sub(protect, text), extensions=['tables'])
    return math_placeholder_pattern.sub(lambda m: formulas[int(m.group(1))], rendered)
