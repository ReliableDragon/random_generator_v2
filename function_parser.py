import re
import logging

from function import Function
from choice_fragment import ChoiceFragment
from common import find_matching_brace
from constants import ARGUMENT_RE

logger = logging.getLogger('function_parser')

class FunctionParser():

    def __init__(self, parse_single_fragment, current_file, line_num):
        self.parse_single_fragment = parse_single_fragment
        # self.choice_parser = choice_parser
        self.current_file = current_file
        self.line_num = line_num

    def parse_function(self, line, num_subchoices):
        # logger.info(f'Parsing function string {line}')
        open_paren = line.find('(')
        close_paren = find_matching_brace('(', ')', open_paren, line)
        function_name = line[:open_paren]
        assert close_paren != -1, f'{self.current_file} line {self.line_num}: No matching close paren found for function {function_name}.'
        args_str = line[open_paren+1:close_paren]
        arg_strs = self.parse_args(args_str, function_name)
        # logger.info(f'Parsed arguments string into arguments: {arg_strs}')
        args = []

        if function_name == '$':
            args.append(ChoiceFragment(value=num_subchoices.get(), type='TEXT'))
            num_subchoices.incr()

        for arg_str in arg_strs:
            fragment_argument, _ = self.parse_single_fragment(arg_str, 0)
            # logger.info(f'Parsed argument into fragment: {fragment_argument}')
            args.append(fragment_argument)

        function = Function(function_name, args)
        error_msg = function.validate()
        assert not error_msg, f'{self.current_file} line {self.line_num}: {error_msg}'

        length = close_paren + 1
        return function, length

    def parse_args(self, arg_str, function_name):
        arguments = []
        idx = 0
        i = 1
        paren_count = 0
        argument = ''
        while idx < len(arg_str):
            ch = arg_str[idx]
            if ch == '(':
                close_paren = find_matching_brace('(', ')', idx, arg_str)
                argument += arg_str[idx:close_paren+1]
                idx = close_paren
            elif ch == ',':
                arguments.append(argument)
                argument = ''
                while idx + 1 < len(arg_str) and arg_str[idx+1] == ' ':
                    idx += 1
            else:
                argument += arg_str[idx]
            idx += 1
        # Append the last argument, unless it ended with a comma.
        if argument:
            arguments.append(argument)
        return arguments
