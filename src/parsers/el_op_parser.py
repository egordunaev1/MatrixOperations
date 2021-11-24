from sympy.parsing.latex import parse_latex, LaTeXParsingError
from parsers.matrix_parser import parse_matrix
from utils import find_close_bracket, Command

import re
import json


def parse_operation(text):
    if re.fullmatch(r'\(\s*\d+\s*(?:col)?\s*\)\s*\\lra\s*\(\s*\d+\s*(?:col)?\s*\)', text):
        n, m = map(int, re.findall(r'\d+', text))
        if text.find('col') != -1:
            return {'axis': 'col', 'op': "n<->m", 'n': n - 1, 'm': m - 1}
        else:
            return {'axis': 'row', 'op': "n<->m", 'n': n - 1, 'm': m - 1}
    elif re.match(r'\(\s*\d+\s*(?:col)?\s*\)\s*\\cdot', text):
        n, k = text.split(r'\cdot', 1)
        n = int(re.search(r'\d+', n).group(0))
        k = parse_latex(k)
        if text.find('col') != -1:
            return {'axis': 'col', 'op': "n->kn", 'n': n - 1, 'k': k}
        else:
            return {'axis': 'row', 'op': "n->kn", 'n': n - 1, 'k': k}
    elif re.fullmatch(r'\(\s*\d+\s*(?:col)?\s*\)\s*[+-]\s*.*?\(\s*\d+\s*(?:col)?\s*\)', text):
        temp = re.findall(r'\(\s*\d+\s*(?:col)?\s*\)', text)
        n, m = int(re.search(r'\d+', temp[0]).group(0)), int(re.search(r'\d+', temp[-1]).group(0))
        k = text[len(temp[0]):len(text) - len(temp[-1])].strip()
        if k in '+-':
            k += '1'
        k = parse_latex(k)
        if text.find('col') != -1:
            return {'axis': 'col', 'op': "n->n+km", 'n': n - 1, 'm': m - 1, 'k': k}
        else:
            return {'axis': 'row', 'op': "n->n+km", 'n': n - 1, 'm': m - 1, 'k': k}
    else:
        raise LaTeXParsingError(f"Cannot parse ({text}) as elementary operation")


def parse_latex_ops(text):
    lines = text.split(r'\\')
    operations = []
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        else:
            operations.append(parse_operation(line))
    return operations


def parse_el_ops(command: Command):
    r"""
    Parses elementary operation command and returns them as list of kwargs for Matrix.row(col)_op.

    Args:
        command (Command): elementary operation command such as the following: \simop, \eqop, \arrop.

    Returns:
        list: list of kwargs for Matrix.row(col)_op
    """

    if command is None:
        raise LaTeXParsingError('Elementary operation command not found')

    if command.name in (r'\simop', r'\arrop', r'\eqop'):
        return parse_latex_ops(command[0].inner)
    else:
        raise LaTeXParsingError("Cannot find correct elementary operation LaTeX command")
