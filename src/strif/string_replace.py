from typing import TypeAlias

Insertion = tuple[int, str]


def insert_multiple(text: str, insertions: list[Insertion]) -> str:
    """
    Insert multiple strings into `text` at the given offsets, at once.
    """
    chunks: list[str] = []
    last_end = 0
    for offset, insertion in sorted(insertions, key=lambda x: x[0]):
        chunks.append(text[last_end:offset])
        chunks.append(insertion)
        last_end = offset
    chunks.append(text[last_end:])
    return "".join(chunks)


Replacement: TypeAlias = tuple[int, int, str]


def replace_multiple(text: str, replacements: list[Replacement]) -> str:
    """
    Replace multiple substrings in `text` with new strings, simultaneously.
    The replacements are a list of tuples (start_offset, end_offset, new_string).
    """
    replacements = sorted(replacements, key=lambda x: x[0])
    chunks: list[str] = []
    last_end = 0
    for start, end, new_text in replacements:
        if start < last_end:
            raise ValueError("Overlapping replacements are not allowed.")
        chunks.append(text[last_end:start])
        chunks.append(new_text)
        last_end = end
    chunks.append(text[last_end:])
    return "".join(chunks)
