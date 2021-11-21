from sympy.parsing.latex import parse_latex, LaTeXParsingError
from utils import find_close_bracket, read_command, Command

import sympy as sp


# Matrix wrapper
class Matrix:
    """Matrix wrapper"""

    def __init__(self, mtype: str, matrix: sp.Matrix, ematrix: sp.Matrix = None):
        self.matrix = matrix
        self.ematrix = ematrix
        self.mtype = mtype

    def __str__(self):
        s = self.mtype + '{\n'
        for row in range(self.matrix.shape[0]):
            s += self.row_to_string(row) + '\n'
        s += '}'
        if self.mtype == r'\ematrix':
            s += '{\n'
            for row in range(self.ematrix.shape[0]):
                s += self.row_to_string(row, False) + '\n'
            s += '}'
        return s

    def row_to_string(self, row: int, main_matrix=True):
        mrow = (self.matrix if main_matrix else self.ematrix).row(row)
        s = ''
        for i in range(len(mrow)):
            parsed = sp.latex(mrow[i])
            s += parsed + ('\\\\' if i == len(mrow) - 1 else '&')
        return s

    def shape(self):
        return self.matrix.shape

    def row_op(self, op, n=None, k=None, m=None):
        """Applies row operations to matrix"""

        kwargs = {'op': op, 'k': k, 'row2': m}
        if op == 'n->kn':
            kwargs['row'] = n
        elif op == 'n<->m':
            kwargs['row1'] = n
        elif op == 'n->n+km':
            kwargs['row'] = n

        self.matrix = self.matrix.elementary_row_op(**kwargs)
        if self.ematrix:
            self.ematrix = self.ematrix.elementary_row_op(**kwargs)

    def col_op(self, op, n=None, k=None, m=None):
        """Applies col operations to matrix"""

        kwargs = {'op': op, 'k': k, 'col2': m}
        if op == 'n->kn':
            kwargs['col'] = n
        elif op == 'n<->m':
            kwargs['col1'] = n
        elif op == 'n->n+km':
            kwargs['col'] = n

        self.matrix = self.matrix.elementary_col_op(**kwargs)
        if self.ematrix:
            self.ematrix = self.ematrix.elementary_col_op(**kwargs)

    def calculate(self):
        """Calculates matrix as part of expression"""

        if self.mtype == 'dmatrix':
            return self.matrix.det()
        elif self.mtype == 'extended':
            raise LaTeXParsingError('Cannot calculate use \\ematrix in expressions')
        else:
            return self.matrix

    def simplify(self):
        self.matrix = self.matrix.simplify()
        if self.ematrix:
            self.ematrix = self.ematrix.simplify()

    def det(self):
        if self.matrix.shape[0] == self.matrix.shape[1]:
            return self.matrix.det()
        else:
            return 0

    def rank(self):
        return self.matrix.rank()

    def inv(self):
        if self.mtype == '\\ematrix':
            raise LaTeXParsingError('Cannot inverse \\ematrix')
        self.matrix = self.matrix.inv()
        return self

    def T(self):
        if self.mtype == '\\ematrix':
            raise LaTeXParsingError('Cannot transpose \\ematrix')
        self.matrix = self.matrix.T
        return self

    def ref(self, reduced: bool):
        matrix = self.matrix
        if self.mtype == '\\ematrix':
            matrix = sp.Matrix.hstack(self.matrix, self.ematrix)
        matrix = matrix.echelon_form() if not reduced else matrix.rref()[0]

        if self.mtype == '\\ematrix':
            left = []
            for i in range(self.shape()[0]):
                left.append(matrix.row(i)[:self.shape()[1]])
            right = []
            for i in range(self.shape()[0]):
                right.append(matrix.row(i)[self.shape()[1]:])
            self.matrix = sp.Matrix(left)
            self.ematrix = sp.Matrix(right)
        else:
            self.matrix = matrix
        return self

def parse_matrix_block(text):
    lines = text.strip().split(r'\\')
    matrix = []
    for line in lines:
        if line == '':
            continue
        try:
            matrix.append(list(map(parse_latex, line.split('&'))))
        except LaTeXParsingError:
            raise LaTeXParsingError(f'LaTeX parser cannot parse row {line}')
    matrix = sp.Matrix(matrix)
    return sp.simplify(matrix)


# Parses one of four matrix tags
def parse_matrix(command: Command):
    r"""
    Parses matrix command and returns Matrix object.

    Args:
        command (Command): matrix command such as the following: \\ematrix, \\matrix, \\dmatrix, \\pmatrix.

    Returns:
        tuple: tuple(amount of blocks parsed, Matrix)
    """

    if command is None:
        raise LaTeXParsingError('Cannot find matrix command')

    if command.name in (r'\matrix', r'\pmatrix', r'\dmatrix'):
        matrix = parse_matrix_block(command[0].inner)
        return 1, Matrix(command.name, matrix)
    elif command.name in (r'\ematrix',):
        matrix1 = parse_matrix_block(command[0].inner)
        matrix2 = parse_matrix_block(command[1].inner)
        return 2, Matrix(command.name, matrix1, matrix2)
    else:
        raise LaTeXParsingError("Not matrix")
