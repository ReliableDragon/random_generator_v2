import re
import logging

from choice_fragment import ChoiceFragment
from equation import Equation
from constants import VARIABLE_REGEX, RESERVED_WORDS
from constants import VALID_ASSIGNMENT_OPS as VALID_OPS

logger = logging.getLogger('assignment')

class Assignment():

    VALID_LHS_RE = VARIABLE_REGEX
    ASSIGNMENT_FNS = {
        ':=': lambda a, b: b,
        '+=': lambda a, b: a + b,
        '-=': lambda a, b: a - b,
        '*=': lambda a, b: a * b,
        '**=': lambda a, b: a ** b,
        '/=': lambda a, b: a / b,
        '//=': lambda a, b: a // b,
    }

    def __init__(self, lhs, op, rhs):
        # Variable-compliant string
        self.lhs = lhs
        # Op-compliant string
        self.op = op
        # Equation
        self.rhs = rhs

    def validate(self):
        lhs = self.lhs
        rhs = self.rhs
        op = self.op

        if op not in VALID_OPS:
            return f'{op} is not a valid operation in an Assignment.'
        if not lhs or not rhs or not op:
            return f'Assignment with lhs={lhs}, rhs={rhs}, and op={op} is invalid. All three must be provided and non-None.'
        if not re.match(VARIABLE_REGEX, lhs):
            return f'Assignment with lhs={lhs} is invalid. Assignment lhs must be valid variable name.'
        if lhs in RESERVED_WORDS:
            return f'Assignment with lhs={lhs} is invalid. {lhs} is a reserved word.'
        if type(rhs) != Equation and rhs != '$':
            return f'Assignment with rhs={rhs} of type {type(rhs)} is invalid. Assignment rhs must be an equation.'
        if op not in VALID_OPS:
            return f'Assignment with op={op} is invalid. Valid ops are {VALID_OPS}.'
        return None

    def evaluate(self, state, evaluate_fragment):
        value = self.rhs.evaluate(evaluate_fragment)
        # logger.info(f'state: {state}, assignment: {self}')

        if not self.lhs in state:
            rtype = type(value)
            if rtype == Equation:
                rtype.get_type()
            if rtype in [int, float, bool]:
                state[self.lhs] = 0
            elif rtype == str:
                state[self.lhs] = ''
            elif rtype == list:
                state[self.lhs] = []
        state[self.lhs] = self.ASSIGNMENT_FNS[self.op](state[self.lhs], value)
        return state

    def __str__(self):
        return f'Assignment[lhs={str(self.lhs)}, op={str(self.op)}, rhs={str(self.rhs)}]'

    def __repr__(self):
        return self.__str__()






# keep buffer
