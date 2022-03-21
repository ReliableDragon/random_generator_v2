

VARIABLE_REGEX = r'([a-zA-Z]\w*)'
NUMBER_RE = r'(\d+(?:\.\d+)?)'
SPECIAL_ARGUMENT_RE = fr'([$@]{VARIABLE_REGEX}*)'
ARGUMENT_RE = fr'({NUMBER_RE}|{SPECIAL_ARGUMENT_RE}|{VARIABLE_REGEX})'
ARGUMENT_WITH_COMMA_RE = fr'({ARGUMENT_RE}, *)'
FUNCTION_REGEX = fr'({VARIABLE_REGEX}\({ARGUMENT_WITH_COMMA_RE}*{ARGUMENT_RE}?\))'
CONTROL_ORDER_REGEX = r'\[\d+\]'
RESERVED_WORDS = ['gauss', 'gamma', 'rand', 'shuffle']

# Make sure the order is '(', ')', or else the opening brace will have higher priority,
# causing the processing loop to try to activate if the closing brace comes up after
# it's already going.
OPS_PRIORITY_LIST = ['(', ')', '?', '<=', '>=', '<', '>', '!=', '==', '-', '+', '^', '//', '/', '*', '**', '!']
VALID_ASSIGNMENT_OPS = [':=', '+=', '-=', '*=', '**=', '/=', '//=']
# In case I forget again, parens don't show up here, they're only relevant
# while you're constructing the Equation tree.
VALID_EQUATION_OPS = ['+', '-', '*', '**', '/', '//', '==', '!=', '>', '<', '>=', '<=', '!', '^', None]
