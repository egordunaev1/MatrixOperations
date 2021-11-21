from sympy.parsing.latex import parse_latex
from parsers.matrix_parser import parse_matrix
from parsers.el_op_parser import parse_el_ops
from utils import normalize_string, find_close_bracket, read_command, Command, skip_spaces, expression_to_string

import sympy as sp
import re
import json


def transpose_replacer(ind, matrices):
    """Tranposes matrix with ^T"""

    replace = 'M_{r_{e_{p_{l_{' + ind + '}}}}}'
    ind = int(ind)
    matrices[ind][1] = matrices[ind][1].T
    return replace


def inverse_replacer(ind, matrices):
    """Inverses matrix with ^{-1}"""

    replace = 'M_{r_{e_{p_{l_{' + ind + '}}}}}'
    ind = int(ind)
    matrices[ind][1] = matrices[ind][1].inv()
    return replace


class Parser:
    custom_commands = {}

    def replace_custom_commands_in_command(self, command: Command, matrices: list = None):
        """
        Replaces all custom commands in provided command's blocks and replaces itself if it's in
        self.custom_commands list. If matrices is not None, replaces them with "M_{r_{e_{p_{l_{index}}}}}"
        and appends parsed matrix in matrices.

        Args:
            command (Command): command with it's blocks.
            matrices (list): either list of matrices to append matrix if the command is matrix or None.

        Returns:
            str: text with performed replaces.
        """

        for i in range(len(command)):
            command[i].inner = self.replace_custom_commands(command[i].inner, matrices is not None)[0]
        if command.name in (r'\matrix', r'\dmatrix', r'\ematrix', r'\pmatrix') and matrices is not None:
            unrel, matrix = parse_matrix(command)
            replace = 'M_{r_{e_{p_{l_{' + str(len(matrices)) + '}}}}}'
            expr = replace
            matrices.append([replace, matrix.calculate()])
        else:
            unrel, replace = self.custom_commands.get(command.name, (0, command.name))
            expr = re.sub(r'#(?P<id>\d+)', lambda x: command[int(x['id']) - 1].inner, replace)
        for i in range(unrel, len(command)):
            expr += '{' + command[i].inner + '}'
        return expr

    def replace_custom_commands(self, text: str, extract_matrices=True):
        """
        Replaces custom latex commands from provided file,
        if extract_matrices=True, it also replaces matrices
        with M_{r_{e_{p_{l_{id}}}}}, and stores parsed matrices
        in dict {Symbol: Matrix}.

        Args:
            text (str): string with normalized LaTeX.
            extract_matrices (bool): flag that indicates whether matrices need to be replaced.

        Returns:
            tuple: tuple(text with performed replaces, list of extracted matrices).
        """

        matrices = [] if extract_matrices else None
        normalized_expr = ''
        pos = 0
        while True:
            nxt = text.find("\\", pos)
            normalized_expr += text[pos: nxt if nxt != -1 else len(text)]
            if nxt == -1:
                return normalized_expr, matrices
            elif nxt != len(text) - 1 and text[nxt + 1] == '\\':
                normalized_expr += '\\\\'
                pos = nxt + 2
                continue
            command = read_command(text, nxt)
            normalized_expr += self.replace_custom_commands_in_command(command, matrices)
            pos = command.end + 1

    def simplify_expr_with_matrices(self, text: str):
        """
        Parses text to expression and simplifies it

        Args:
            text (str): string with raw LaTeX.

        Returns:
            str: simplified expression as LaTeX string.
        """

        text = normalize_string(text)
        text, matrices = self.replace_custom_commands(text)

        text = re.sub(r'M_{r_{e_{p_{l_{(?P<ind>\d+)}}}}}\^{?\s*T\s*}?',
                      lambda x: transpose_replacer(x['ind'], matrices), text)
        text = re.sub(r'M_{r_{e_{p_{l_{(?P<ind>\d+)}}}}}\^{\s*-1\s*}', lambda x: inverse_replacer(x['ind'], matrices),
                      text)

        expr = parse_latex(text).subs(
            [(sp.Symbol(m[0]), sp.MatrixSymbol(m[0], *m[1].shape)) for m in reversed(matrices)])
        expr = expr.subs([(sp.MatrixSymbol(m[0], *m[1].shape), m[1]) for m in matrices])

        return expression_to_string(expr.expand().simplify())

    def inv(self, text: str):
        """
        Parses text with matrix from LaTeX, inverses matrix and returns it as LaTeX string.

        Args:
            text (str): raw LaTeX code with matrix.


        Returns:
            str: inverse matrix.
        """

        text = normalize_string(text).strip()
        text = self.replace_custom_commands(text, False)[0]
        command = read_command(text, 0)
        matrix = parse_matrix(command)[1]
        return str(matrix.inv())

    def transpose(self, text: str):
        """
        Parses text with matrix from LaTeX, transposes matrix and returns it as LaTeX string.

        Args:
            text (str): raw LaTeX code with matrix.

        Returns:
            str: transposed matrix.
        """

        text = normalize_string(text).strip()
        text = self.replace_custom_commands(text, False)[0]
        command = read_command(text, 0)
        matrix = parse_matrix(command)[1]
        return str(matrix.T())

    def ref(self, text: str, reduced: bool = False):
        """
        Parses text with matrix from LaTeX and returns it's REF or RREF as LaTeX string.

        Args:
            reduced (bool): REF or RREF
            text (str): raw LaTeX code with matrix.

        Returns:
            str: REF matrix.
        """

        text = normalize_string(text).strip()
        text = self.replace_custom_commands(text, False)[0]
        command = read_command(text, 0)
        matrix = parse_matrix(command)[1]
        return str(matrix.ref(reduced))

    def info(self, text: str):
        """
        Parses text with matrix from LaTeX and returns matrix' determinant and rank.

        Args:
            text (str): raw LaTeX code with matrix.

        Returns:
            str: string which contains determinant and rank.
        """

        text = normalize_string(text).strip()
        text = self.replace_custom_commands(text, False)[0]
        command = read_command(text, 0)
        matrix = parse_matrix(command)[1]

        return f'det: {matrix.det()}, rank: {matrix.rank()}'

    def apply_elementary_operations(self, text: str):
        r"""
        Applies elementary operations to matrix.

        Allowed operations:

        * (n)+k(m)
        * (n)\\cdot k
        * (n)\\lra(m)

        You can make column operation by adding "col" into parentheses i.e. (1col) or (1 col)

        Args:
            text (str): raw LaTeX code with matrix and elementary operations such as \\simop, \\eqop, \\arrop.

        Returns:
            str: matrix with applied ops as LaTeX string.
        """

        text = normalize_string(text).strip()
        text = self.replace_custom_commands(text, False)[0]

        command = read_command(text, 0)
        blocks, matrix = parse_matrix(command)
        pos = command[blocks - 1].end + 1
        pos = skip_spaces(text, pos)
        ops = parse_el_ops(read_command(text, pos))

        for op in ops:
            axis = op.pop('axis')
            if axis == 'col':
                matrix.col_op(**op)
            else:
                matrix.row_op(**op)
        matrix.simplify()

        return str(matrix)

    def parse_command_file(self, text):
        r"""
        Reads, parses and stores in self.custom_commands all "\\newcommand" tags from text.

        Args:
            text (str): content of file with custom commands.
        """

        text = text.replace('\n', '')
        pattern = re.compile(r"\\newcommand\s*{\s*(?P<name>\\[a-zA-Z]+)\s*}\s*(?:\[(?P<args_cnt>[0-9]+)])?\s*")
        for i in pattern.finditer(text):
            closing = find_close_bracket(text, i.end(), not_found_exception=False)
            if closing != -1:
                self.custom_commands[i['name']] = (
                    int(i['args_cnt']) if i['args_cnt'] else 0, text[i.end() + 1: closing])
        matrices = (r'\dmatrix', r'\ematrix', r'\matrix', r'\pmatrix')
        el_ops = (r'\arrop', r'\eqop', r'\simop')
        for m in matrices + el_ops:
            if m in self.custom_commands:
                self.custom_commands.pop(m)

    def __init__(self, custom_command_file: str = ''):
        """Initialization with custom command file"""

        custom_command_file = custom_command_file.strip()
        if custom_command_file:
            try:
                f = open(custom_command_file, 'r', encoding='utf-8')
            except OSError:
                raise OSError(f"Unable to open/read file: {custom_command_file}")

            with f:
                self.parse_command_file(f.read())
