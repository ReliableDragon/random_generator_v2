import re
import logging

from choice_fragment import ChoiceFragment
from function import Function
from function_parser import FunctionParser
from subchoice_counter import SubchoiceCounter
from common import find_matching_brace
from constants import VARIABLE_REGEX, RESERVED_WORDS

logger = logging.getLogger('choice_parser')

class ChoiceParser():

    def __init__(self, current_file, line_num):
        self.current_file = current_file
        self.line_num = line_num
        self.num_subchoices = SubchoiceCounter()

    def parse_choice_data(self, line):
        fragments = []
        idx = 0
        text = ''
        while idx < len(line):
            # logging.info(f'line: {line}, idx: {idx} ({line[idx]})')
            fragment, length = self.parse_single_fragment(line, idx)
            idx += length
            logging.info(f'fragment generated: {fragment}')
            fragments.append(fragment)
        # logger.info(f'Fragments: {fragments}')
        return fragments

    def parse_single_fragment(self, line, idx):
        idx = idx
        text = ''
        length = None
        if line[idx] == '$':
            fragment, length = self.parse_subchoice_fragment(line, idx)
            # logging.info(f'parse_subchoice_fragment.length: {length}')
            self.num_subchoices.incr()
        elif line[idx] =='@':
            fragment, length = self.parse_control_fragment(line, idx)
            # logging.info(f'parse_control_fragment.length: {length}')
        else:
            sc_loc = line.find('$', idx)
            if sc_loc == -1:
                sc_loc = len(line)
            cf_loc = line.find('@', idx)
            if cf_loc == -1:
                cf_loc = len(line)
            nearest_char = min(sc_loc, cf_loc)
            fragment = ChoiceFragment(line[idx:nearest_char])
            length = nearest_char - idx
        # logging.info(f'length: {length}')
        assert length, f'parse_single_fragment is stalled. This should never happen.'
        return fragment, length

    def parse_subchoice_fragment(self, line, idx=0):
        line = line[idx+1:]
        length = 1
        bracket_re = re.match(r'\[\d+\]', line)
        space_re = re.match(r'\d+(?: |$)', line)
        if bracket_re:
            subchoice_end = bracket_re.end()
            order = int(line[1:subchoice_end])
            line = line[subchoice_end+1:]
            # +1 to account for 0-indexing
            length += subchoice_end+1
        elif space_re:
            subchoice_end = space_re.end()
            order = line[1:subchoice_end]
            # No +1 because it's cancelled out by the -1 to not consume the space/EOL.
            length += subchoice_end
        else:
            order = 'NONE'
        return ChoiceFragment(value=self.num_subchoices.count, order=order, type='SUBCHOICE'), length

    def parse_control_fragment(self, line, idx=0):
        order = 'NONE'
        line = line[idx+1:]
        length = 1

        if re.match(CONTROL_ORDER_REGEX, line):
            open_brace = 0
            close_brace = find_matching_brace('[', ']', 0, line)
            order = int(line[open_brace+1:close_brace])
            idx = close_brace + 1
            assert idx < len(line) and (line[idx].isalpha() or line[idx] == '['), f'{self.current_file} line {self.line_num}: Control statement @{line[open_brace:close_brace+1]} had order override, but did not contain an actual control statement following it.'

        line = line[idx]
        length += idx

        if line[0] == '[':
            type = 'EXPRESSION'
            value, next_idx, type = self.parse_expression(self, line, parse)
        else:
            value, next_idx, type = self.parse_var_or_func(self, line)
        length += next_idx
        return ChoiceFragment(value=value, type=type, order=order), length

    def parse_var_or_func(self, line):
        # Variables and functions can be called "naked" provided the next character is non-word.
        variable_re = re.match(VARIABLE_REGEX, line)
        if not variable_re:
            assert bool(variable_re), f'{self.current_file} line {self.line_num}: Invalid variable starting @{line[:10]}.'
        name_end = variable_re.end()

        if len(line) > name_end and line[name_end] == '(':
            function_parser = FunctionParser(
                    self.parse_single_fragment,
                    self.current_file,
                    self.line_num)
            # WARNING: THIS MODIFIES num_subchoices BY REFERENCE. It's terrible,
            # but it was the least bad way of splitting out the function parsing
            # code that I could come up with.
            value, next_idx = function_parser.parse_function(line, self.num_subchoices)
            type = 'FUNCTION'
        else:
            # We don't add one here, because we don't want to consume the space/EOL.
            next_idx = name_end
            value = line[:next_idx]
            assert value not in RESERVED_WORDS, f'{self.current_file} line {self.line_num}: {value} is a reserved word, and cannot be used as a variable name.'
            type = 'VARIABLE'
        return value, next_idx, type

    def parse_expression(self, line):
        '''
        Allows: Mathematical expressions, state get/set/modify, order customization, function calls, import calls, subcalls. Yikes.
        Let's start at the beginning, I guess.
        '''
        close_bracket = find_matching_brace('[', ']', 0, line)
        assert close_bracket != -1, f'{self.current_file} line {self.line_num}: Mismatched expression braces: {line}.'
        expression_parser = ExpressionParser(self.parse_single_fragment, self.current_file, self.line_num, self.parse_var_or_func)
        value, next_idx = expression_parser.parse_expression(line)

        return value, next_idx, 'EXPRESSION'
        #ChoiceFragment(value=value, type='EXPRESSION'),




# keep buffer
