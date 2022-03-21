from choice_fragment import ChoiceFragment
from constants import VALID_EQUATION_OPS as VALID_OPS

class Equation():

    UNARY_FNS = {
        '+': int,
        '-': lambda a: a * -1,
        '!': lambda a: not a,
    }
    BINARY_FNS = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '**': lambda a, b: a ** b,
        '/': lambda a, b: a / b,
        '//': lambda a, b: a // b,
        '==': lambda a, b: a == b,
        '!=': lambda a, b: a != b,
        '>': lambda a, b: a > b,
        '<': lambda a, b: a < b,
        '>=': lambda a, b: a >= b,
        '<=': lambda a, b: a <= b,
        '?': lambda a, b: b if a else '',
    }



    def __init__(self, rhs, lhs=None, op=None):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
        # Have to do this one at run time, since it references itself.
        self.VALID_VALUES = [int, float, bool, str, ChoiceFragment, Equation]

    def get_type(self):
        t = type(self.rhs)
        if t == Equation:
            return self.rhs.get_type()
        else:
            return t

    # The one big thing we can't do here is validate ChoiceFragments, since it's
    # dynamic whether, say, a variable is an int or a string or an array.
    def validate(self):
        lhs = self.lhs
        rhs = self.rhs
        op = self.op

        if not lhs and not rhs and not op:
            return f'All values are empty!'

        if op not in VALID_OPS:
            return f'{op} is not a valid operation in an Equation.'
        if rhs not in self.VALID_VALUES:
            return f'{rhs} is not a valid value in an Equation.'
        if lhs not in self.VALID_VALUES:
            return f'{lhs} is not a valid value in an Equation.'

        rtype = type(rhs)
        ltype = type(lhs)
        if ltype == Equation:
            ltype = lhs.get_type()
        if rtype == Equation:
            rtype = rhs.get_type()

        if rhs and rtype != ChoiceFragment and lhs and ltype != ChoiceFragment:
            conversion_safe = False
            if ltype in [int, float, bool, str] and rtype in [int, float, bool]:
                conversion_safe = True
            if not conversion_safe:
                return f'{rhs} (of type {rtype}) is on the right-hand side of {lhs}, but cannot be converted to {ltype}.'

        if lhs and not rhs:
            return f'Got equation with lhs={lhs} and no rhs. This is invalid! Perhaps you meant to set the lhs as the rhs?'
        if lhs and rhs and not op:
            return f'Got equation with lhs={lhs} and rhs={rhs}, but no operation to combine them!'

        if not lhs and rhs and op not in ['+', '-', '!']:
            return f'Got equation with only rhs={rhs}, but binary operation op={op} was provided!'
        if lhs and rhs and op == '!':
            return f'Got equation with lhs={lhs} and rhs={rhs}, but unary operation op={op} was provided!'

        if ltype == bool and op in ['/', '//']:
            return f'Got equation with boolean values lhs={lhs} and rhs={rhs}, but an operation op={op} that\'s invalid on booleans!'
        if ltype == str and rtype == str and op in ['/', '//', '*', '**', '-', '!', '^']:
            return f'Got equation with string values lhs={lhs} and rhs={rhs}, but an operation op={op} that\'s invalid on strings!'
        if ltype == str and rtype == int and op != '*':
            return f'Got equation with string/int mixed values lhs={lhs} and rhs={rhs}, but an operation op={op} other than multiplication!'
        return None

    def evaluate(self):
        if lhs.get_type() == Equation:
            self.lhs = lhs.evaluate()
        if rhs.get_type() == Equation:
            self.rhs = rhs.evaluate()

        lhs = self.lhs
        rhs = self.rhs
        op = self.op

        if lhs == None and op == None:
            return rhs
        if lhs == None:
            return self.UNARY_FNS[op](rhs)
        else:
            return self.BINARY_FNS[op](lhs, rhs)

    def __str__(self):
        return f'Equation[lhs: {str(self.lhs)}, op={str(self.op)}, rhs={str(self.rhs)}]'

    def __repr__(self):
        return self.__str__()







# save buffer
