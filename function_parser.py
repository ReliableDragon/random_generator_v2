import re
import logging

from function import Function
from choice_fragment import ChoiceFragment
from constants import ARGUMENT_RE

logger = logging.getLogger('function_parser')

class FunctionParser():

    def __init__(self, parse_subchoice_fragment, parse_control_fragment, current_file, line_num):
        self.parse_subchoice_fragment = parse_subchoice_fragment
        self.parse_control_fragment = parse_control_fragment
        # self.choice_parser = choice_parser
        self.current_file = current_file
        self.line_num = line_num

    def parse_function(self, line, num_subchoices):
        logger.info(f'Parsing function string {line}')
        open_paren = line.find('(')
        close_paren = line.find(')', open_paren)
        function_name = line[:open_paren]
        assert close_paren != -1, f'{self.current_file} line {self.line_num}: No matching close paren found for function {function_name}.'
        arg_strs = self.parse_args(line, open_paren, close_paren, function_name)
        args = []

        for arg_str in arg_strs:
            fragment_argument = None
            if arg_str[0] == '$':
                fragment_argument, _ = self.parse_subchoice_fragment(arg_str)
                num_subchoices.incr()
            elif arg_str[0] == '@':
                fragment_argument, _ = self.parse_control_fragment(arg_str)
            else:
                fragment_argument = ChoiceFragment(arg_str)

            args.append(fragment_argument)
        function = Function(function_name, args)
        error_msg = function.validate()
        assert not error_msg, error_msg

        end_idx = close_paren + 1
        return function, end_idx

    def parse_args(self, line, open_paren, close_paren, function_name):
        arguments_str = line[open_paren+1:close_paren]
        arguments = []
        idx = 0
        i = 1
        while idx < len(arguments_str):
            while arguments_str[idx] == ' ':
                idx += 1
            arg_end = arguments_str.find(',', idx)
            if arg_end == -1:
                arg_end = len(arguments_str)
            arg_str = arguments_str[idx:arg_end]
            assert re.match(ARGUMENT_RE, arg_str), f'{self.current_file} line {self.line_num}: Argument #{i} for function @{line[:close_paren]} is improperly formatted.'
            arguments.append(arg_str)
            idx = arg_end + 1
        return arguments
