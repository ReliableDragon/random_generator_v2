import re

from equation_parser import EquationParser
from choice_fragment import ChoiceFragment
from common import find_matching_brace

class WeightParser():

    def __init__(self, parse_var_or_func, num_subchoices, current_file, line_num):
        self.parse_var_or_func = parse_var_or_func
        self.num_subchoices = num_subchoices
        self.current_file = current_file
        self.line_num = line_num

    def parse_weight(self, line):
        weight_type, next_idx = self.get_weight_type(line)
        assert weight_type != 'INVALID', f'{self.current_file} line {self.line_num}: Choice "{line}" must begin with a valid weight!'
        if weight_type == 'NUMERIC':
            weight_re = re.match(r'\d+', line)
            weight = int(line[:weight_re.end()])
        elif weight_type.find('EQUATION') != -1:
            # Strip the at-sign and brackets
            equation = line[2:next_idx-1]
            equation_parser = EquationParser(self.parse_var_or_func, self.num_subchoices, self.current_file, self.line_num)
            weight = equation_parser.parse_equation(equation)
            assert weight.get_type() in [int, ChoiceFragment], f'{self.current_file} line {self.line_num}: Choice "{line}" begins with an expression weight, but expression evaluates type {weight.get_type()} instead of int (or var)!'

        remainder = line[next_idx:]
        # Gotta check remainder because a weight-only line is valid.
        while remainder and remainder[0] == ' ':
            remainder = remainder[1:]
        return weight, weight_type, remainder

    # TODO: Figure out how to add percentile weights, to make randomly generating
    # an assortment of things easier.
    def get_weight_type(self, line):
        numeric_re = re.match(r'\d+ ', line)
        numeric_eol_re = re.match(r'\d+\n', line)
        # numeric_percentile_re = re.match(r'\d+%', line)
        if line[0] == '@':
            assert line[1] == '[', f'{self.current_file} line {self.line_num}: Choice "{line}" starts with equation weight, but no opening brace found.'
            close_brace = find_matching_brace('[', ']', 1, line)
            assert close_brace != -1, f'{self.current_file} line {self.line_num}: Choice "{line}" starts with equation weight, but no closing brace found.'
            assert line[:close_brace+1].find('$') == -1, f'{self.current_file} line {self.line_num}: Choice "{line}" starts with equation weight, but references subchoice. This is invalid for weight expressions.'
            # if len(line) > close_brace + 1 and line[close_brace + 1] == '%':
            #     return 'PERCENTILE_EQUATION', close_brace + 2
            # else:
            return 'EQUATION', close_brace + 1
        # Number followed by space
        elif numeric_re:
            return 'NUMERIC', numeric_re.end()
        # Number on empty line
        elif numeric_eol_re:
            return 'NUMERIC', numeric_eol_re.end()
        # elif numeric_percentile_re:
        #     return 'NUMERIC_PERCENTILE', numeric_percentile_re.end()
        return 'INVALID', -1
