import re

from choice_fragment import ChoiceFragment
from equation import Equation
from constants import VARIABLE_REGEX, RESERVED_WORDS

class Assignment():

    VALID_LHS_RE = VARIABLE_REGEX
    VALIP_OPS = ['=', '+=', '-=', '*=', '**=', '/=', '//=']
    ASSIGNMENT_FNS = {
        '=': lambda a, b: b,
        '+=' lambda a, b: a + b,
        '-=' lambda a, b: a - b,
        '*=' lambda a, b: a * b,
        '**=' lambda a, b: a ** b,
        '/=' lambda a, b: a / b,
        '//=' lambda a, b: a // b,
    }

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def validate(self):
        lhs = self.lhs
        rhs = self.rhs
        op = self.op

        if not lhs or not rhs or not op:
            return f'Assignment with lhs={lhs}, rhs={rhs}, and op={op} is invalid. All three must be provided and non-None.'
        if not re.match(VARIABLE_REGEX, lhs):
            return f'Assignment with lhs={lhs} is invalid. Assignment lhs must be valid variable name.'
        if lhs in RESERVED_WORDS:
            return f'Assignment with lhs={lhs} is invalid. {lhs} is a reserved word.'
        if type(rhs) != Equation and rhs != '$':
            return f'Assignment with rhs={rhs} of type {type(rhs)} is invalid. Assignment rhs must be an expression.'
        if op not in self.VALID_OPS:
            return f'Assignment with op={op} is invalid. Valid ops are {self.VALID_OPS}.'
        return None

    def evaluate(self, state):
        if not self.lhs in state:
            rtype = self.rhs.get_type()
            if rtype in [int, float, bool, ChoiceFragment]:
                state[self.lhs] = 0
            if rtype == str:
                state[self.lhs] = ''

        value = self.rhs.evaluate()
        state[self.lhs] = self.ASSIGNMENT_FNS[self.op](state[self.lhs], rhs)






# keep buffer
