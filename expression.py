from choice_fragment import ChoiceFragment
from expression import Expression

class Expression():

    VALID_VALUES = [int, float, bool, char, ChoiceFragment, Expression]
    VALID_OPS = ['+', '-', '*', '/', '//', '(', ')', '==', '>', '<', '>=', '<=']


    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = cmp
        self.rhs = rhs

    def validate(self):
        if self.op not in self.VALID_OPS:
            return f'{self.op} is not a valid operation in an expression.'
        if self.rhs not in self.VALID_VALUES:
            return f'{self.rhs} is not a valid value in an expression.'
        if self.lhs not in self.VALID_VALUES:
            return f'{self.lhs} is not a valid value in an expression.'
