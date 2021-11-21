import re
import string
import sympy as sp

from sympy.parsing.latex.errors import LaTeXParsingError


class Command:
    """LaTeX command wrapper"""

    class Block:
        def __init__(self, inner: str, begin: int, end: int):
            self.inner = inner
            self.begin = begin
            self.end = end

    def append_block(self, inner, begin, end):
        self.blocks.append(self.Block(inner, begin, end))
        self.end = end

    def __len__(self):
        return len(self.blocks)

    def __getitem__(self, ind):
        if 0 <= ind < len(self.blocks):
            return self.blocks[ind]
        raise LaTeXParsingError(f"Unable to find block number {ind}")

    def __setitem__(self, key, value):
        self.blocks[key] = value

    def __init__(self, name, pos):
        self.blocks = []
        self.name = name
        self.begin = pos
        self.end = pos + len(name) - 1


def find_close_bracket(text, pos=0, bracket='{}', not_found_exception=True):
    """Finds close bracket for the open one which is on the pos or returns either exceptions or -1 depending on
    not_found_exception argument"""

    opened = 0
    for i in range(pos, len(text)):
        if text[i] in bracket:
            if text[i] == bracket[0]:
                opened += 1
            elif text[i] == bracket[1]:
                opened -= 1

            if not opened:
                return i
    if not_found_exception:
        raise LaTeXParsingError("Matching close bracket not found")
    else:
        return -1


def skip_spaces(text: str, pos: int):
    while pos < len(text) and text[pos] == ' ':
        pos += 1
    return pos


def read_command(text: str, pos: int):
    if pos >= len(text) or text[pos] != '\\':
        return None

    begin = pos
    pos += 1

    while pos < len(text) and text[pos].isalpha():
        pos += 1
    name = text[begin:pos]

    command = Command(name, begin)

    if pos != len(text) and text[pos] not in "(){}[]\\ ":
        raise LaTeXParsingError(f"Unexpected symbol after {command.name}: '{text[pos]}'")
    pos = skip_spaces(text, pos)

    while pos < len(text) and text[pos] == '{':
        begin = pos
        pos = find_close_bracket(text, pos)
        command.append_block(text[begin + 1:pos], begin, pos)
        pos = skip_spaces(text, pos + 1)
    return command


def normalize_string(s: str):
    return s.translate(str.maketrans({i: ' ' for i in string.whitespace}))


def matrix_replacer(expr):
    return '\matrix{\n' + expr['inner'] + '\n}'


def expression_to_string(expr):
    expr = sp.latex(expr)
    expr = re.sub(r'\\left(?P<l>\()|\\right(?P<r>\))', r'\g<l>\g<r>', expr)
    pattern = re.compile(r'\\left\[\\begin{matrix}(?P<inner>.+?)\\end{matrix}\\right]')
    expr = re.sub(pattern, matrix_replacer, expr).replace('\\\\', '\\\\\n')
    return expr
