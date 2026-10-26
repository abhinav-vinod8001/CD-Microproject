"""
Bidirectional Translator between Malayalam and English Programming Keywords.
Preserves variables, numbers, operators, comments, indentation, and string literals.
"""

import re
from typing import Dict
from .tokens import MALAYALAM_TO_ENGLISH, ENGLISH_TO_MALAYALAM


TOKEN_REGEX = re.compile(
    r'(\"(?:[^\"\\\\]|\\\\.)*\"|\'(?:[^\'\\\\]|\\\\.)*\')|'               # Group 1: String literals
    r'(#.*|//.*)|'                                                         # Group 2: Comments
    r'([a-zA-Z_\u0D00-\u0D7F][a-zA-Z0-9_\u0D00-\u0D7F\u200C\u200D]*)|'   # Group 3: Words / Identifiers
    r'(\s+|[^\s\w]+)',                                                    # Group 4: Whitespace and symbols
    re.UNICODE
)


def translate_code(code: str, direction: str = "to_english") -> str:
    """
    Translates keywords in code.
    direction can be 'to_english' or 'to_malayalam'.
    """
    is_to_eng = (direction == "to_english")
    mapping: Dict[str, str] = MALAYALAM_TO_ENGLISH if is_to_eng else ENGLISH_TO_MALAYALAM

    result_pieces = []
    pos = 0
    length = len(code)

    while pos < length:
        match = TOKEN_REGEX.match(code, pos)
        if not match:
            result_pieces.append(code[pos])
            pos += 1
            continue

        str_literal, comment, word, other = match.groups()

        if str_literal is not None:
            # Preserve string literals exactly as-is
            result_pieces.append(str_literal)
        elif comment is not None:
            # Preserve comments exactly as-is
            result_pieces.append(comment)
        elif word is not None:
            key = word if is_to_eng else word.lower()
            if key in mapping:
                result_pieces.append(mapping[key])
            else:
                result_pieces.append(word)
        elif other is not None:
            # Preserve indentation, newlines, and operators
            result_pieces.append(other)

        pos = match.end()

    return "".join(result_pieces)
