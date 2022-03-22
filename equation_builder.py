import logging

from constants import OPS_PRIORITY_LIST
from equation import Equation

logger = logging.getLogger('equation_builder')

class EquationBuilder():
    def __init__(self, current_file, line_num):
        self.current_file = current_file
        self.line_num = line_num

    def build_eq_tree(self, tokens):
        op_stack = []
        val_stack = []
        # logger.info(f'tokens: {tokens}')

        for i, tk in enumerate(tokens):
            # logger.info(f'Processing token "{tk}".')
            if tk not in OPS_PRIORITY_LIST:
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
        if type(result_eq) != Equation:
            # Single value, never got a chance to wrap it
            result_eq = Equation(rhs=result_eq)
        # logger.info(f'Resultant equation: {result_eq}')
        return result_eq


    def priority(self, op):
        if type(op) == Equation:
            op = Equation.op
        if op == None:
            return -1
        return OPS_PRIORITY_LIST.index(op)
