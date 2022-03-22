import logging

from choice_fragment import ChoiceFragment
from constants import VALID_EQUATION_OPS as VALID_OPS
from constants import EQUATION_COMPARATOR_OPS as COMPARATOR_OPS

logger = logging.getLogger('equation')

class Equation():

    UNARY_FNS = {
        '+': int,
        '-': lambda a: a * -1,
        '!': lambda a: not a,
    }
    BINARY_FNS = {
        '+': lambda a, b: a + b,
        '++': lambda a, b: str(a) + str(b),
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
        self.VALID_TYPES = [int, float, bool, str, ChoiceFragment, Equation]

    def get_type(self):
        if self.op == '++':
            return str
        ltype = type(self.lhs)
        if ltype == Equation:
            ltype = self.lhs.get_type()
        rtype = type(self.rhs)
        if rtype == Equation:
            rtype = self.rhs.get_type()

        if self.op == '*' and ltype in [str, ChoiceFragment] and rtype == int:
            # Not technically true. This could be anything when ltype is ChoiceFragment,
            # but CF is our best wildcard.
            return ltype

        return rtype

    # The one big thing we can't do here is validate ChoiceFragments, since it's
    # dynamic whether, say, a variable is an int or a string or an array.
    def validate(self):
        logger.info(f'Validating equation {self}.')
        lhs = self.lhs
        rhs = self.rhs
        op = self.op

        if not lhs and not rhs and not op:
            return f'All values are empty!'
        if lhs and not rhs:
            return f'Got equation with lhs={lhs} and no rhs. This is invalid! Perhaps you meant to set the lhs as the rhs?'
        if lhs and rhs and not op:
            return f'Got equation with lhs={lhs} and rhs={rhs}, but no operation to combine them!'

        if type(rhs) not in self.VALID_TYPES:
            return f'{rhs} is not a valid value in an Equation.'
        if op and op not in VALID_OPS:
            return f'{op} is not a valid operation in an Equation.'
        if lhs and type(lhs) not in self.VALID_TYPES:
            return f'{lhs} is not a valid value in an Equation.'

        rtype = type(rhs)
        ltype = type(lhs)
        if ltype == Equation:
            ltype = lhs.get_type()
        if rtype == Equation:
            rtype = rhs.get_type()
        logger.info(f'ltype: {ltype}, rtype: {rtype}')

        if rhs and rtype != ChoiceFragment and lhs and ltype != ChoiceFragment:
            conversion_safe = False
            if ltype in [int, float, bool, str] and rtype in [int, float, bool]:
                conversion_safe = True
            if not conversion_safe:
                return f'{rhs} (of type {rtype}) is on the right-hand side of {lhs}, but cannot be converted to {ltype}.'

        if not lhs and rhs and op and op not in ['+', '-', '!']:
            return f'Got equation with only rhs={rhs}, but binary operation op={op} was provided!'
        if lhs and rhs and op == '!':
            return f'Got equation with lhs={lhs} and rhs={rhs}, but unary operation op={op} was provided!'

        if ltype == bool and op in ['/', '//']:
            return f'Got equation with boolean values lhs={lhs} and rhs={rhs}, but an operation op={op} that\'s invalid on booleans!'
        if ltype == str and rtype == str and op in ['/', '//', '*', '**', '-', '!', '^']:
            return f'Got equation with string values lhs={lhs} and rhs={rhs}, but an operation op={op} that\'s invalid on strings!'
        if ltype == str and rtype == int and op != '*' and op not in COMPARATOR_OPS:
            return f'Got equation with string/int mixed values lhs={lhs} and rhs={rhs}, but an operation op={op} other than multiplication/comparison!'
        return None

    def evaluate(self, evaluate_fragment):
        ltype = type(self.lhs)
        rtype = type(self.rhs)
        logger.info(f'Equation pre-recursion: {self}. lhs_type = {ltype}, rhs_type = {rtype}.')

        # TODO: Consider if this is the best approach. I like that it only calls
        # out to the main generator when necessary, but don't love the two custom
        # classes in the equation tree.
        if ltype == ChoiceFragment:
            self.lhs = evaluate_fragment(self.lhs)
        elif ltype == Equation:
            self.lhs = self.lhs.evaluate(evaluate_fragment)
        if rtype == ChoiceFragment:
            self.rhs = evaluate_fragment(self.rhs)
        elif rtype == Equation:
            self.rhs = self.rhs.evaluate(evaluate_fragment)
        logger.info(f'Equation post-recursion: {self}')

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
        return f'Equation[lhs={str(self.lhs)}, op={str(self.op)}, rhs={str(self.rhs)}]'

    def __repr__(self):
        return self.__str__()







# save buffer
