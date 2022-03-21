import math
import logging

from equation import Equation

from constants import OPS_PRIORITY_LIST
from choice_fragment import ChoiceFragment
from function import Function
from equation_builder import EquationBuilder

logger = logging.getLogger('equation_parser')

class EquationParser():

    def __init__(self, parse_var_or_func, num_subchoices, current_file, line_num):
        self.parse_var_or_func = parse_var_or_func
        self.num_subchoices = num_subchoices
        self.current_file = current_file
        self.line_num = line_num

    def parse_equation(self, eq_str):
        eq_str = eq_str.replace(' ', '')
        eq_str = eq_str.lower()
        idx = 0
        tokens = []
        last_tk_type = None
        while idx < len(eq_str):
            tk, last_tk_type, next_idx = self.get_next_token(eq_str, idx, last_tk_type)
            idx = next_idx
            # logger.info(f'idx: {idx}')
            tokens.append(tk)
        assert tokens, f'{self.current_file} line {self.line_num}: Attempted to parse equation, but did not find any tokens after parsing.'
        equation_builder = EquationBuilder(self.current_file, self.line_num)
        return equation_builder.build_eq_tree(tokens)

    def get_tk_type(self, ch):
        if ch in OPS_PRIORITY_LIST + ['=']:
            tk_type = 'OP'
        elif ch == '"':
            tk_type = 'ALPHA'
        elif ch.isnumeric():
            tk_type = 'NUM'
        elif ch == '.':
            tk_type = 'FLOAT'
        elif ch == '#':
            tk_type = 'VAR'
        elif ch == '$':
            tk_type = 'SUB'
        else:
            raise ValueError(f'Token at index {idx} in string {eq_str} is not identifiable as any valid token type.')
        return tk_type

    def process_one_char(self, tk, ch, tk_type, last_tk_type, idx):
        value = None
        # Total hack. I don't want to deal with dual binary/unary operations right now though.
        if tk == '-' and ch.isnumeric() and last_tk_type == 'OP':
            tk_type = 'NUM'
            tk += ch
            idx += 1
        elif tk_type == 'NUM' and ch == '.':
            tk_type = 'FLOAT'
            tk += ch
            idx += 1
        elif tk_type == 'OP' and tk and tk + ch in OPS_PRIORITY_LIST:
            value = tk + ch
            idx += 1
        elif tk_type == 'OP' and tk in OPS_PRIORITY_LIST and tk + ch not in OPS_PRIORITY_LIST:
            value = tk
        elif tk_type == 'NUM' and not ch.isnumeric():
            value = int(tk)
        elif tk_type == 'FLOAT' and not ch.isnumeric():
            value = float(tk)
        elif tk in ['true', 'false'] and not ch.isalpha():
            value = bool(tk)
            tk_type = 'BOOL'
        elif tk_type == 'ALPHA' and ch == '"':
            value = tk + ch
            idx += 1
        elif tk_type == 'VAR' and ch == '(':
            tk_type = 'FUNC'
        elif tk_type == 'FUNC' and ch == ')':
            value = tk + ch
            idx += 1
        elif tk_type == 'SUB' and tk == '$' and ch != '(':
            value = tk
        elif tk_type == 'SUB' and ch == ')':
            value = tk + ch
            idx += 1
        elif tk_type == 'VAR' and (not ch.isalnum() or ch == '_'):
            value = tk
        else:
            tk += ch
            idx += 1
        return tk, tk_type, value, idx

    def get_next_token(self, eq_str, idx, last_tk_type):
        start_idx = idx
        tk = ''
        tk_type = None
        done = False
        value = None
        ch = eq_str[idx]
        # logger.info(f'ch: {ch}')
        tk_type = self.get_tk_type(ch)

        tk += ch
        idx += 1
        # logger.info(f'value: {value}')
        while value == None and idx < len(eq_str):
            ch = eq_str[idx]
            # logger.info(f'idx: {idx}')
            # logger.info(f'tk: {tk}')
            # logger.info(f'ch: {ch}')
            tk, tk_type, value, idx = self.process_one_char(tk, ch, tk_type, last_tk_type, idx)
        # If we're cut short, such as by reaching the end, we won't have hit a
        # lookahead trigger, but we still know that the token is valid as long
        # as the equation is well-formed.
        if value == None:
            value = tk

        # USE VALUE BELOW. tk is unreliable at this point, as it may or may not
        # contain the final character of the token.
        if tk_type in ['VAR', 'FUNC']:
            if tk_type == 'FUNC':
                assert value[-1] == ')', f'{self.current_file} line {self.line_num}: Attempted to parse equation, but got unclosed parentheses for function call starting at index {start_idx}.'
            # logger.info(f'Processing token {value}.')
            value = value[1:]
            frag_value, _, type = self.parse_var_or_func(value)
            value = ChoiceFragment(value=frag_value, type=type)
        elif value in ['true', 'false']:
            value = bool(value)
            tk_type = 'BOOL'
        elif tk_type == 'NUM':
            value = int(value)
        elif tk_type == 'FLOAT':
            value = float(value)
        elif tk_type == 'SUB':
            # logger.info(f'SUB token: {value}')
            open_paren = value.find('(')
            args = [self.num_subchoices.get()]
            if open_paren != -1:
                assert value[-1] == ')', f'{self.current_file} line {self.line_num}: Attempted to parse equation, but got unclosed parentheses for subchoice call starting at index {start_idx}.'
                repetition = int(value[open_paren+1:-1])
                args.append(repetition)
            value = ChoiceFragment(value=Function(name='$', args=args), type='FUNCTION')
            self.num_subchoices.incr()
        elif tk_type == 'ALPHA':
            assert value[-1] == '"', f'{self.current_file} line {self.line_num}: Attempted to parse equation, but got unclosed string starting at index {start_idx}.'
            value = value[1:-1]

        # logger.info(f'Generated token "{tk}" of type {tk_type}')
        return value, tk_type, idx








# keep buffer
