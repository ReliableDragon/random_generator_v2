import re
import logging

from assignment import Assignment
from constants import VALID_ASSIGNMENT_OPS as VALID_OPS
from constants import VARIABLE_REGEX
# from equation import Equation
from choice_fragment import ChoiceFragment
from equation_parser import EquationParser

logger = logging.getLogger('assignment_parser')

class AssignmentParser():

    def __init__(self, parse_single_fragment, num_subchoices, current_file, line_num):
        self.parse_single_fragment = parse_single_fragment
        self.num_subchoices = num_subchoices
        self.current_file = current_file
        self.line_num = line_num

    def parse_assignment(self, line):
        # logger.info(f'Parsing assignment {line}')
        for op in VALID_OPS:
            if op in line:
                parts = line.split(op)

                assert len(parts) == 2, f'{self.current_file} line {self.line_num}: Expression in line {line} had op {op}, but didn\'t have values on both sides.'

                var_name, eq_str = parts
                var_name = var_name.strip(' ')
                eq_str = eq_str.strip(' ')

                assert var_name[0] == '#', f'{self.current_file} line {self.line_num}: Expression in line {line} must begin with a variable starting with "#".'

                var_name = var_name[1:]

                assert re.match(VARIABLE_REGEX, var_name), f'{self.current_file} line {self.line_num}: Expression in line {line} has improper variable name following the "#".'
                # lhs = self.parse_single_fragment(var)

                equation_parser = EquationParser(self.parse_single_fragment, self.num_subchoices, self.current_file, self.line_num)
                rhs = equation_parser.parse_equation(eq_str)
                # if type(rhs) == ChoiceFragment:
                #     # Equation was simple enough it was processed as a ChoiceFragment,
                #     # so we need to wrap it.
                #     rhs = Equation(rhs=rhs)

                assignment = Assignment(lhs=var_name, op=op, rhs=rhs)
                validation_error = assignment.validate()
                assert not validation_error, f'{self.current_file} line {self.line_num}: {validation_error}'
                return assignment
        raise ValueError(f'{self.current_file} line {self.line_num}: Expression in line {line} had no valid operator.')
