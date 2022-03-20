import math
import logging

from equation import Equation

logger = logging.getLogger('equation_parser')

class EquationParser():

    # Make sure the order is '(', ')', or else the opening brace will have higher priority,
    # causing the processing loop to try to activate if the closing brace comes up after
    # it's already going.
    OPS_PRIORITY_LIST = ['(', ')', '<=', '>=', '<', '>', '!=', '==', '-', '+', '^', '//', '/', '*', '**', '!']

    def __init__(self, current_file, line_num):
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
        return self.build_eq_tree(tokens)

    def build_eq_tree(self, tokens):
        op_stack = []
        val_stack = []
        # logger.info(f'tokens: {tokens}')

        for i, tk in enumerate(tokens):
            # logger.info(f'Processing token "{tk}".')
            if tk not in self.OPS_PRIORITY_LIST:
                # Seed val_stack
                if not val_stack:
                    val_stack.append(tk)
                    # logger.info(f'Before: val_stack: {val_stack}, op_stack: {op_stack}')
                    continue
                assert op_stack, f'{self.current_file} line {self.line_num}: Attempted to parse equation {tokens}, but got value {tk} without a valid operator to act on it near {tokens[i-1:i+2]}.'

                val_stack.append(tk)
                if i != len(tokens) - 1:
                    stack_priority = self.priority(op_stack[-1])
                    next_token = tokens[i+1]
                    next_token_priority = self.priority(next_token)
                    # logger.info(f'stack_priority: {stack_priority}, next_token_priority: {next_token_priority}')
                while op_stack and (i == len(tokens)-1 or (stack_priority >= next_token_priority)):
                    # logger.info(f'Creating equation with current token.')
                    # logger.info(f'Before: val_stack: {val_stack}, op_stack: {op_stack}')
                    rhs = val_stack.pop()
                    assert val_stack, f'{self.current_file} line {self.line_num}: Attempted to parse equation {tokens}, but got invalid result. (Do you have two operators next to each other, or otherwise forget a value somewhere?)'
                    lhs = val_stack.pop()
                    op = op_stack.pop()
                    new_eq = Equation(lhs=lhs, rhs=rhs, op=op)
                    val_stack.append(new_eq)
                    # logger.info(f'After: val_stack: {val_stack}, op_stack: {op_stack}')
                    if op_stack and i != len(tokens)-1:
                        stack_priority = self.priority(op_stack[-1])
                        next_token_priority = self.priority(tokens[i+1])
                        # logger.info(f'stack_priority: {stack_priority}, next_token_priority: {next_token_priority}')
            # OP
            else:
                if op_stack and op_stack[-1] == '(' and tk == ')':
                    op_stack.pop()
                    continue
                op_stack.append(tk)

        assert not op_stack and len(val_stack) == 1, f'{self.current_file} line {self.line_num}: Attempted to parse equation {tokens}, but got invalid stacks at the end of parsing:\nop_stack: {op_stack}\nval_stack: {val_stack}.'
        result_eq = val_stack[0]
        # logger.info(f'Resultant equation: {result_eq}')
        return result_eq

    def priority(self, op):
        if type(op) == Equation:
            op = Equation.op
        if op == None:
            return -1
        return self.OPS_PRIORITY_LIST.index(op)

    def get_next_token(self, eq_str, idx, last_tk_type):
        tk = ''
        tk_type = None
        done = False
        value = None
        ch = eq_str[idx]
        # logger.info(f'ch: {ch}')
        if ch in self.OPS_PRIORITY_LIST + ['=']:
            tk_type = 'OP'
        elif ch.isalpha():
            tk_type = 'ALPHA'
        elif ch.isnumeric():
            tk_type = 'NUM'
        elif ch == '.':
            tk_type = 'FLOAT'
        elif ch == '#':
            tk_type = 'VAR'
        else:
            raise ValueError(f'Token at index {idx} in string {eq_str} is not identifiable as any valid token type.')

        tk += ch
        idx += 1
        # logger.info(f'value: {value}')
        while value == None and idx < len(eq_str):
            ch = eq_str[idx]
            # logger.info(f'idx: {idx}')
            # logger.info(f'tk: {tk}')
            # logger.info(f'ch: {ch}')
            # Total hack. I don't want to deal with dual binary/unary operations right now though.
            if tk == '-' and ch.isnumeric() and last_tk_type == 'OP':
                tk_type = 'NUM'
                tk += ch
                idx += 1
            elif tk_type == 'NUM' and ch == '.':
                tk_type = 'FLOAT'
                tk += ch
                idx += 1
            elif tk_type == 'OP' and tk and tk + ch in self.OPS_PRIORITY_LIST:
                value = tk + ch
                idx += 1
            elif tk_type == 'OP' and tk in self.OPS_PRIORITY_LIST and tk + ch not in self.OPS_PRIORITY_LIST:
                value = tk
            # elif tk_type == 'OP':
            #     raise IllegalArgumentError(f'All ops should be two characters max, but we got {tk + ch}.')
            elif tk_type == 'NUM' and not ch.isnumeric():
                value = int(tk)
            elif tk_type == 'FLOAT' and not ch.isnumeric():
                value = float(tk)
            elif tk in ['true', 'false'] and not ch.isalpha():
                value = bool(tk)
                tk_type = 'BOOL'
            elif tk_type == 'ALPHA' and not ch.isalpha():
                value = tk
            elif tk_type == 'VAR' and ch == '(':
                tk_type = 'FUNC'
            elif tk_type == 'FUNC' and ch == ')':
                value = tk + ch
                idx += 1
            elif tk_type == 'VAR' and (not ch.isalnum() or ch == '_'):
                value = tk
            else:
                tk += ch
                idx += 1
        # If we're cut short, such as by reaching the end, we won't have hit a
        # lookahead trigger, but we still know that the token is valid as long
        # as the equation is well-formed.
        if value == None:
            value = tk

        # logger.info(f'Generated token "{tk}" of type {tk_type}')
        return value, tk_type, idx








# keep buffer
