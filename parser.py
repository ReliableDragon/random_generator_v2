import re
import os
import logging

from root_choice import RootChoice
from choice import Choice
from choice_fragment import ChoiceFragment
from choice_parser import ChoiceParser
from constants import VARIABLE_REGEX, FUNCTION_REGEX

logger = logging.getLogger('parser')


class Parser():

    VARIABLE_REGEX = r'([a-zA-Z]\w*)'
    NUMBER_RE = r'(\d+(?:\.\d+)?)'
    ARGUMENT_RE = fr'({NUMBER_RE}|{VARIABLE_REGEX})'
    ARGUMENT_WITH_COMMA_RE = fr'({ARGUMENT_RE}, *)'
    FUNCTION_REGEX = fr'({VARIABLE_REGEX}\({ARGUMENT_WITH_COMMA_RE}*{ARGUMENT_RE}?\))'

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
        imports, data = self.parse_imports(data)
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
        choice_parser = ChoiceParser(self.current_file, self.line_num)
        weight, weight_type, remainder = choice_parser.parse_weight(line)
        fragments = choice_parser.parse_choice_data(remainder)
        return Choice(weight, fragments, nesting)

    def parse_imports(self, data):
        if data[0] == '\n':
            # logger.info(f'No imports found, short circuiting imports for {self.current_file}.')
            # No imports, we're currently on the blank line. Consume it and return.
            return {}, data[1:]
        # logger.info(f'Data: {data}')
        import_block_end = data.find('\n\n')
        # logger.info(f'imports: {data[:import_block_end]}')
        assert import_block_end != -1, f'{self.current_file} line {self.line_num}: Expected blank line after name and imports.'
        imports = {}
        eol = data.find('\n')
        line = data[:eol]
        self.line_num += 1
        while eol <= import_block_end:
            # logger.info(f'Import: {line}')
            name, _import = self.parse_import(line)
            imports[name] = _import

            new_eol = data.find('\n', eol+1)
            line = data[eol+1:new_eol]
            eol = new_eol
            self.line_num += 1
        # +2 to skip the newlines. Note we're already on the 2nd newline, to be > import_block_end.
        post_import_data = data[eol+1:]
        # logger.info(f'Post import data: {post_import_data}')
        # logger.info(f'Imports: {imports}')
        return imports, post_import_data

    def parse_import(self, import_line):
        # logger.info(f'importing: {import_line}')
        assert ':' in import_line, f'{self.current_file} line {self.line_num}: Import {import_line} does not contain a colon.'
        name, filename = import_line.split(':')
        assert re.match(self.VARIABLE_REGEX, name), f'{self.current_file} line {self.line_num}: Import name {name} does not match pattern of a-zA-Z_.'

        # Save line_num while we recurse.
        line_num = self.line_num
        _import = self.parse_file(filename)
        self.line_num = line_num
        return name, _import

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
        stripped_lines = [l.rstrip(' ') for l in lines]
        no_trailing_spaces = '\n'.join(stripped_lines)
        return no_trailing_spaces


def get_nesting(line):
    num_spaces = len(line) - len(line.lstrip(' '))
    return num_spaces // 2
