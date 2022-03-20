import re

from expression import Expression
from common import find_matching_brace
from assignment import VALID_OPS as VALID_ASSIGNMENT_OPS
from equation import VALID_OPS as VALID_EQUATION_OPS

# Nesting expressions is currently not permitted. Not sure if there's a use for it.
class ExpressionParser():

    def __init__(self, parse_single_fragment, current_file, line_num,  parse_var_or_func):
        self.parse_single_fragment = parse_single_fragment
        self.current_file = current_file
        self.line_num = line_num
        self.parse_var_or_func =  parse_var_or_func

    def parse_expression(self, line):
        order = 'NONE'
        open_brace = 0
        close_brace = find_matching_brace('[', ']', 0, line)
        expr_start = open_brace + 1
        expr_end = close_brace - 1
        expr_str = line[expr_start:expr_end+1]

        if re.match(r'\d+', expr_str):
            order = int(expr_str)
            assert line[close_brace+1] == '[', f'{self.current_file} line {self.line_num}: Expression {expr_str} had order override, but did not contain an actual expression following it.'
            open_brace = close_brace+1
            close_brace = find_matching_brace('[', ']', open_brace, line)
            expr_start = open_brace + 1
            expr_end = close_brace - 1
            expr_str = line[expr_start:expr_end+1]

        clause_strs = expr_str.split(';')
        clause_strs = [clause_str.strip() for clause_str in clause_strs]
        clauses = [self.parse_clause(clause_str) for clause_str in clause_strs]
        next_idx = close_brace + 1
        return clauses

    '''
    Clauses can be Equations, Assignments, Strings, Variables, or Functions.
    TODO: Consider allowing expressions to reference chosen values.
    '''
    def parse_clause(self, clause_str):
        for op in VALID_ASSIGNMENT_OPS:
            if op in clause_str:
                return self.parse_assignment(clause_str)
        for op in VALID_EQUATION_OPS:
            if op in clause_str:
                result_eq = self.parse_equation(clause_str)
                return ChoiceFragment(type='EQUATION', value=result_eq)
        if clause_str[0] == '"' and clause_str[-1] == '"':
            return self.parse_expr_string(clause_str)
        else:
            value, _, type = self.parse_var_or_func(clause_str)
            return ChoiceFragment(value=value, type='type')










# keep buffer
