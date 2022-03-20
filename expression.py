from choice_fragment import ChoiceFragment
from expression import Expression

class Expression():

    # In case I forget again, parens don't show up here, they're only relevant
    # while you're constructing the expression tree.
    VALID_VALUES = [int, float, bool, str, ChoiceFragment, Expression]
    VALID_OPS = ['+', '-', '*', '**', '/', '//', '==', '!=', '>', '<', '>=', '<=', '!', '^', None]
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
    }



    def __init__(self, lhs=None, op=None, rhs=None):
        self.lhs = lhs
        self.op = cmp
        self.rhs = rhs

    def get_type(self):
        t = type(self.lhs)
        if t == Expression:
            return self.lhs.get_type()
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

        if op not in self.VALID_OPS:
            return f'{op} is not a valid operation in an expression.'
        if rhs not in self.VALID_VALUES:
            return f'{rhs} is not a valid value in an expression.'
        if lhs not in self.VALID_VALUES:
            return f'{lhs} is not a valid value in an expression.'

        rtype = type(rhs)
        ltype = type(lhs)
        if ltype == Expression:
            ltype = lhs.get_type()
        if rtype == Expression:
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
        if ltype == str and rtype == int and op in != '*':
            return f'Got equation with string/int mixed values lhs={lhs} and rhs={rhs}, but an operation op={op} other than multiplication!'

    def evaluate(self):
        if lhs.get_type() == Expression:
            self.lhs = lhs.evaluate()
        if rhs.get_type() == Expression:
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




# save buffer
