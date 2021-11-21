from parsers.latex_parser import Parser
from sympy.parsing.latex.errors import LaTeXParsingError

import argparse
import json


def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', type=str, help="File with custom latex commands ('\\newcommand' commands)")
    return arg_parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    try:
        parser = Parser(args.file)
    except OSError as e:
        parser = Parser()
        print(e)

    while True:
        s = ''
        while s.strip() == '':
            s = input()

        inp = json.loads(s)
        command = inp['command']
        text = inp['text']

        response = {
            'command': command,
            'id': inp['id'],
        }

        try:
            if command == 'el_ops':
                response['res'] = text + '\n' + parser.apply_elementary_operations(text)
            elif command == 'simplify':
                response['res'] = parser.simplify_expr_with_matrices(text)
            elif command == 'matrix_info':
                response['res'] = parser.info(text)
            elif command == 'transpose':
                response['res'] = parser.transpose(text)
            elif command == 'inverse':
                response['res'] = parser.inv(text)
            elif command == 'ref':
                response['res'] = parser.ref(text, False)
            elif command == 'rref':
                response['res'] = parser.ref(text, True)
            print(json.dumps(response))
        except Exception as e:
            print(json.dumps({'command': 'error', 'res': str(e)}))
