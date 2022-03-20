

class ChoiceFragment():

    '''
    Value is the text value for type='TEXT', the expression object for type='EXPRESSION',
    the variable name for type='VARIABLE', and the function object for type='FUNCTION',
    and the (0-based) index of the corresponding choice group for type='SUBCHOICE'. Can
    also contain the sub-expression objects 'EQUATION', 'ASSIGNMENT', and 'STRING', which
    have Equation, Assignment, and ExprString objects in the value field, respectively.
    '''
    def __init__(self, value=None, order='NONE', type='TEXT'):
        self.value = value
        self.type = type
        self.order = order

    def __str__(self):
        return f'ChoiceFragment[value: "{self.value}", type: {self.type}, order: {self.order}]'

    def __repr__(self):
        return self.__str__()
