from choice_fragment import ChoiceFragment
from expression import Expression

class Equation():

    VALID_RHS = [int, float, bool, char, ChoiceFragment, Expression]
    VALID_OPS = ['+', '-', '*', '/', '//', '(', ')', '==', '>', '<', '>=', '<=']


    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.cmp = cmp
        self.rhs = rhs

    def validate(self):
        
