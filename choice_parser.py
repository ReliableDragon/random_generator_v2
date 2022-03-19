import re
import logging

from choice_fragment import ChoiceFragment
from function import Function
from constants import VARIABLE_REGEX, FUNCTION_REGEX

logger = logging.getLogger('choice_parser')

class ChoiceParser():

    def __init__(self, current_file, line_num):
        self.current_file = current_file
        self.line_num = line_num
    # assert weight_type != "INVALID", f'{self.current_file} line {self.line_num}: Choice "{line}" must begin with a valid weight!'
    def parse_choice_data(self, line):
        fragments = []
        idx = 0
        text = ''
        num_subchoices = 0
        while idx != len(line):
            ch = line[idx]
            if ch in ['$', '@']:
                text_fragment = ChoiceFragment(text)
                text = ''
                fragments.append(text_fragment)

                if ch == '$':
                    fragment, length = self.parse_subchoice_fragment(line, idx, num_subchoices)
                    num_subchoices += 1
                elif ch == '@':
                    fragment, length = self.parse_control_fragment(line, idx)

                fragments.append(fragment)
                idx += length
            else:
                text += ch
                idx += 1
        if text:
            text_fragment = ChoiceFragment(text)
            fragments.append(text_fragment)

        # logger.info(f'Fragments: {fragments}')
        return fragments

    def parse_subchoice_fragment(self, line, idx, num_subchoices):
        line = line[idx+1:]
        length = 1
        bracket_re = re.match(r'\[\d+\]', line)
        space_re = re.match(r'\d+(?: |$)', line)
        if bracket_re:
            subchoice_end = bracket_re.end()
            order = line[1:subchoice_end-1]
            line = line[subchoice_end+1:]
            # +1 to account for 0-indexing
            length += subchoice_end+1
        elif space_re:
            subchoice_end = space_re.end()
            order = line[1:subchoice_end-1]
            # No +1 because it's cancelled out by the -1 to not consume the space.
            length += subchoice_end
        else:
            order = 'NONE'
        return ChoiceFragment(value=num_subchoices, order=order, type='SUBCHOICE'), length

    def parse_control_fragment(self, line, idx):
        line = line[idx+1:]
        length = 1
        # expression_re = re.match(r'\[\.*\]', line)
        # assert bool(expression_re) ^ bool(variable_re) ^ bool(function_re), f'{self.current_file} line {self.line_num}: Choice "{line}" has invalid control sequence starting {line[:10]}!'

        if line[0] == '[':
            # Not implemented
            raise NotImplementedError('Expressions are not yet implemented!')
        else:
            # Variables and functions can be called "naked" provided the next character is non-word.
            variable_re = re.match(VARIABLE_REGEX, line)
            if not variable_re:
                assert bool(variable_re), f'{self.current_file} line {self.line_num}: Invalid variable starting @{line[:10]}.'
            name_end = variable_re.end()
            if len(line) > name_end and line[name_end] == '(':
                function_re = re.match(FUNCTION_REGEX, line)
                assert bool(function_re), f'{self.current_file} line {self.line_num}: Invalid function call: @{variable_re.group()}.'
                control_end = function_re.end()
                type = 'FUNCTION'
                value = self.parse_function(line[:control_end])
            else:
                control_end = name_end
                type = 'VARIABLE'
                value = line[:control_end]
            # No +1 because it's cancelled out by the -1 to not consume the space.
            length += control_end
            return ChoiceFragment(value=value, type=type), length

    def parse_function(self, function_str):
        logger.info(f'Parsing function string {function_str}')
        open_paren = function_str.find('(')
        name = function_str[:open_paren]
        args = []
        idx = open_paren + 1
        while idx < len(function_str):
            # logger.info(f'idx: {idx}')
            while function_str[idx] == ' ':
                idx += 1
            arg_end = function_str.find(',', idx)
            if arg_end == -1:
                arg_end = function_str.find(')', idx)
            assert arg_end != -1, f'{self.current_file} line {self.line_num}: Could not find end for argument {len(args)} in function "{function_str}".'
            args.append(function_str[idx:arg_end])
            idx = arg_end + 1
        function = Function(name, args)
        error_msg = function.validate()
        assert not error_msg, error_msg
        return function

    def parse_weight(self, line):
        weight_type = self.get_weight_type(line)
        assert weight_type != "INVALID", f'{self.current_file} line {self.line_num}: Choice "{line}" must begin with a valid weight!'
        if weight_type == "NUMERIC":
            re_result = re.match(r'\d+', line)
            end_idx = re_result.end()
            weight = int(line[:end_idx])
            remainder = line[end_idx+1:]
            # Gotta check remainder because a weight-only line is valid.
            while remainder and remainder[0] == ' ':
                remainder = remainder[1:]
            return weight, weight_type, remainder

    def get_weight_type(self, line):
        # Number followed by space
        if re.match(r'\d+ ', line):
            return "NUMERIC"
        # Number on empty line
        elif re.match(r'\d+$', line):
            return "NUMERIC"
        return "INVALID"
