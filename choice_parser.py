import re
import logging

from choice_fragment import ChoiceFragment
from function import Function
from function_parser import FunctionParser
from subchoice_counter import SubchoiceCounter
from constants import VARIABLE_REGEX, FUNCTION_REGEX, ARGUMENT_RE

logger = logging.getLogger('choice_parser')

class ChoiceParser():

    def __init__(self, current_file, line_num):
        self.current_file = current_file
        self.line_num = line_num
        self.num_subchoices = SubchoiceCounter()
    # assert weight_type != "INVALID", f'{self.current_file} line {self.line_num}: Choice "{line}" must begin with a valid weight!'
    def parse_choice_data(self, line):
        fragments = []
        idx = 0
        text = ''
        while idx != len(line):
            ch = line[idx]
            if ch in ['$', '@']:
                text_fragment = ChoiceFragment(text)
                text = ''
                fragments.append(text_fragment)

                if ch == '$':
                    fragment, length = self.parse_subchoice_fragment(line, idx)
                    self.num_subchoices.incr()
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

    def parse_subchoice_fragment(self, line, idx=0):
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
        return ChoiceFragment(value=self.num_subchoices.count, order=order, type='SUBCHOICE'), length

    def parse_control_fragment(self, line, idx=0):
        line = line[idx+1:]
        length = 1

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
                function_parser = FunctionParser(
                        self.parse_subchoice_fragment,
                        self.parse_control_fragment,
                        self.current_file,
                        self.line_num)
                # WARNING: THIS MODIFIES num_subchoices BY REFERENCE. It's terrible,
                # but it was the least bad way of splitting out the function parsing
                # code that I could come up with.
                value, end_idx = function_parser.parse_function(line, self.num_subchoices)
                type = 'FUNCTION'
            else:
                end_idx = name_end
                value = line[:end_idx]
                type = 'VARIABLE'
            # No +1 because it's cancelled out by the -1 to not consume the space.
            length += end_idx
            return ChoiceFragment(value=value, type=type), length
