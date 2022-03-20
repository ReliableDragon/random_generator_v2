import re
import os
import logging

from root_choice import RootChoice
from choice import Choice
from choice_fragment import ChoiceFragment
from choice_parser import ChoiceParser
from weight_parser import WeightParser
from import_parser import ImportParser
from common import skip_comments
from constants import VARIABLE_REGEX

logger = logging.getLogger('parser')

class Parser():

    def __init__(self, dir_path):
        self.line_num = 1
        self.current_file = None
        self.dir_path = dir_path

    def parse_file(self, filename):
        self.line_num = 1
        old_file = self.current_file
        self.current_file = filename
        filepath = os.path.join(self.dir_path, filename)
        file = open(filepath)
        data = file.read()

        data = self.preprocess_data(data)
        data = self.parse_name(data)
        import_parser = ImportParser(self.current_file, self.line_num)
        imports, data, self.line_num = import_parser.parse_imports(data, self.parse_file)
        imports = imports
        blocks = self.parse_blocks(data)

        choice_blocks = []
        for block in blocks:
            choice_blocks.append(self.parse_choice_block(block))
        self.current_file = old_file
        # logger.info(f'Choice Blocks: {choice_blocks}')
        # logger.info(f'Parsed imports: {imports}')
        return choice_blocks, imports

    def parse_choice_block(self, block):
        root_choice = RootChoice()
        idx = 0
        # logger.info(f'\nBlock:\n{block}\nEnd block.')
        eol = block.find('\n')
        if eol == -1:
            eol = len(block)

        # logger.info(f'eol: {eol}')
        # Use <= bc ending nl is optional
        while idx <= len(block):
            # logger.info(f'idx: {idx}')
            line = block[idx:eol]
            # logger.info(f'line: "{line}"')
            self.line_num += 1

            nesting = get_nesting(line)
            root_choice.set_nesting(nesting)
            line = line.lstrip(' ')
            # logger.info(f'Nesting is {nesting}.')

            assert line, f'{self.current_file} line {self.line_num}: Expected non-blank line.'

            if line[0] == ';':
                continue

            if line == '$':
                root_choice.add_choice_group()
            else:
                root_choice.add_choice(self.parse_choice(line, nesting))

            idx = eol + 1
            eol = block.find('\n', idx+1)
            if eol == -1:
                eol = len(block)

            # logger.info(f'Root Choice: {root_choice}')
        # Skip extra blank line after each block
        self.line_num += 1

        return root_choice
            # logger.info(f'root_choice)

    def parse_choice(self, line, nesting):
        # logger.info(f'Line: {line}')
        weight_parser = WeightParser(self.current_file, self.line_num)
        weight, weight_type, remainder = weight_parser.parse_weight(line)
        choice_parser = ChoiceParser(self.current_file, self.line_num)
        fragments = choice_parser.parse_choice_data(remainder)
        return Choice(weight, fragments, nesting)

    def parse_name(self, data):
        assert data.find('\n'), f'line {self.line_num}: Expected list name at start of file on its own line.'
        eol = data.find('\n')
        name = data[:eol]
        # logger.info(f'Name: {name}')
        # +1 to consume newline
        return data[eol+1:]

    def parse_blocks(self, data):
        blocks = data.split('\n\n')
        # strip empty line in case of file ending with no newline
        blocks[-1] = blocks[-1].rstrip('\n')
        # logger.info(f'blocks)
        return blocks

    def preprocess_data(self, data):
        lines = data.split('\n')
        # Remove trailing whitespace and comments. Yes one-lining is bad practice. It's in a low-touch function though, and it's fun.
        stripped_lines = [l.rstrip(' ') for l in lines if not (len(l.lstrip(' ')) > 1 and l.lstrip(' ')[:2] == '//')]
        processed_data = '\n'.join(stripped_lines)
        # logger.info(f'Post processing data: {processed_data}')
        return processed_data


def get_nesting(line):
    num_spaces = len(line) - len(line.lstrip(' '))
    return num_spaces // 2
