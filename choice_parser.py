import re
import logging

from choice_fragment import ChoiceFragment
from function import Function
from function_parser import FunctionParser
from subchoice_counter import SubchoiceCounter
from common import find_matching_brace
from parse_error import ParseError
from expression_parser import ExpressionParser
from constants import VARIABLE_REGEX, RESERVED_WORDS, CONTROL_ORDER_REGEX

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
            # logger.info(f'Parsing choice data in line: {line[idx:]}')
            try:
                fragment, length = self.parse_single_fragment(line[idx:])
                # logger.info(f'PCD idx: {idx}, length: {length}')
            except ParseError as e:
                logger.fatal(f'Error encountered in file {self.current_file} at line {self.line_num} ({line}): {e.msg}')
                raise
            idx += length
            # logging.info(f'fragment generated: {fragment}')
            # logging.info(f'new index: {idx} makes line {line[idx:]}')
            fragments.append(fragment)
        # logger.info(f'Fragments: {fragments}')
        return fragments

    def parse_single_fragment(self, line):
        text = ''
        length = None
        # logger.info(f'Parsing line "{line}"')
        if line[0] in ['$', '@', '#']:
            sym = line[0]
            line = line[1:]
            length = 1

            order, or_length, line = self.get_order_override(line, sym)
            # logger.info(f'Parsed order override {order}, remaining line "{line}"')
            length += or_length
            call_length = 0
            if sym == '$':
                # Special case if we call $ as a function.
                if line and line[0] == '(':
                    fragment, call_length = self.parse_var_or_func_call('$' + line, order)
                    # -1 because we're adding an extra character
                    call_length -= 1
                else:
                    fragment = ChoiceFragment(value=self.num_subchoices.count, order=order, type='SUBCHOICE')
                # logging.info(f'parsed subchoice fragment: {fragment}')
                self.num_subchoices.incr()
            # elif line[idx] =='@':
            #     fragment, length = self.parse_control_fragment(line, idx)
            elif sym == '@':
                fragment, call_length = self.parse_expression_call(line, order)
            elif sym == '#':
                fragment, call_length = self.parse_var_or_func_call(line, order)
            length += call_length

            # logging.info(f'parse_control_fragment.length: {length}')
        else:
            # Text fragment
            if line[0] == '"':
                end_text = line.find('"', 1)
                start_text = 1
            else:
                sc_loc = line.find('$')
                if sc_loc == -1:
                    sc_loc = len(line)
                ex_loc = line.find('@')
                if ex_loc == -1:
                    ex_loc = len(line)
                vf_loc = line.find('#')
                if vf_loc == -1:
                    vf_loc = len(line)
                start_text = 0
                end_text = min(sc_loc, ex_loc, vf_loc)
            fragment = ChoiceFragment(line[start_text:end_text])
            length = end_text
        # logging.info(f'length: {length}')
        if not length:
            raise ParseError(f'parse_single_fragment is stalled. This should never happen.')
        return fragment, length

    # returns: ChoiceFragment:parsed, int:length
    def parse_var_or_func_call(self, line, order, idx=0):
        # logger.info(f'Parsing var/func fragment in line "{line[idx:]}"')
        # Variables and functions can be called "naked" provided the next character is non-word.
        variable_re = re.match(VARIABLE_REGEX, line)
        name_end = None
        if not variable_re:
            if line[0] == '$':
                name_end = 1
            else:
                raise ParseError(f'{self.current_file} line {self.line_num}: Invalid variable on line {line}.')
        else:
            name_end = variable_re.end()

        if len(line) > name_end and line[name_end] == '(':
            type = 'FUNCTION'
            function_parser = FunctionParser(
                    self.parse_single_fragment,
                    self.current_file,
                    self.line_num)
            # WARNING: THIS MODIFIES num_subchoices BY REFERENCE. It's terrible,
            # but it was the least bad way of splitting out the function parsing
            # code that I could come up with.
            value, length = function_parser.parse_function(line, self.num_subchoices)
        else:
            type = 'VARIABLE'
            # We don't add one here, because we don't want to consume the space/EOL.
            length = name_end
            value = line[:length]
            if value in RESERVED_WORDS:
                raise ParseError(f'{self.current_file} line {self.line_num}: {value} is a reserved word, and cannot be used as a variable name.')
        # length += call_length
        # logger.info(f'Parsed fragment {line[idx:length]} of length {length}')
        return ChoiceFragment(value=value, type=type, order=order), length

    def get_order_override(self, line, sym):
        order = 'NONE'
        length = 0
        name_dict = {
            '$': 'subchoice',
            '#': 'variable/function',
            '@': 'expression'
        }
        name = name_dict[sym]
        if re.match(CONTROL_ORDER_REGEX, line):
            # logger.info('Found expression.')
            open_brace = 0
            close_brace = find_matching_brace('[', ']', 0, line)
            order = int(line[open_brace+1:close_brace])
            length = close_brace + 1
            # length += next_idx
            invalid_vf_override = sym == '#' and (length >= len(line) or not (line[length].isalpha() or line[length] == '$'))
            invalid_expr_override = sym == '@' and (length >= len(line) or line[length] != '[')
            if not sym != '$' and (invalid_expr_override or invalid_vf_override):
                raise ParseError(f'{self.current_file} line {self.line_num}: {name} in line {line} had order override from characters {open_brace} to {close_brace} ("{line[open_brace:close_brace+1]}"), but did not contain an actual {name} following it.')
            line = line[length:]
        return order, length, line

    def parse_expression_call(self, line, order, idx=0):
        '''
        Allows: Mathematical expressions, state get/set/modify, order customization, function calls, import calls, subcalls. Yikes.
        Let's start at the beginning, I guess.
        '''
        assert line[0] == '[', f'{self.current_file} line {self.line_num} ({line}): Expression call made, but no brackets found!'
        # TODO: Should this go in expression_parser instead?
        close_bracket = find_matching_brace('[', ']', 0, line)
        if close_bracket == -1:
            raise ParseError(f'{self.current_file} line {self.line_num}: Mismatched expression braces: {line}.')
        expression_parser = ExpressionParser(self.parse_single_fragment, self.current_file, order, self.line_num, self.num_subchoices)
        value, length = expression_parser.parse_expression(line)
        # logger.info(f'Parsed expression "{line[:length]}"')

        # logger.info(f'Parsed fragment {line[idx:length]}')
        return ChoiceFragment(value=value, type='EXPRESSION', order=order), length




# keep buffer
