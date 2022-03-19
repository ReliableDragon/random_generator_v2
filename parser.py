import re
import os

from root_choice import RootChoice
from choice import Choice

class Parser():

    def __init__(self, dir_path):
        self.line_num = 1
        self.current_file = None
        self.imports = []
        self.dir_path = dir_path


    def parse_file(self, filename):
        old_file = self.current_file
        self.current_file = filename
        filepath = os.path.join(self.dir_path, filename)
        file = open(filepath)
        data = file.read()
        data = self.preprocess_data(data)
        # if self.current_file == 'shop_test.rg2':
        #     print(f'Processed data: {data}')
        data = self.parse_name(data)
        # if self.current_file == 'shop_test.rg2':
        #     print(f'Processed data: {data}')
        self.imports, data = self.parse_imports(data)
        # if self.current_file == 'shop_test.rg2':
        #     print(f'Processed data: {data}')
        blocks = self.parse_blocks(data)
        choice_blocks = []
        for block in blocks:
            choice_blocks.append(self.parse_choice_block(block))
        self.current_file = old_file
        return choice_blocks
        # print(choice_blocks)

    def parse_choice_block(self, block):
        choice = RootChoice()
        idx = 0
        # print(f'\nBlock:\n{block}\nEnd block.')
        eol = block.find('\n')
        # Use <= bc ending nl is optional
        while idx <= len(block):
            line = block[idx:eol]
            # print(f'line: {line}')
            self.line_num += 1

            nesting = get_nesting(line)
            choice.set_nesting(nesting)
            line = line.lstrip(' ')
            # print(f'Nesting is {nesting}.')

            if line[0] == ';':
                continue

            if line == '$':
                choice.add_choice_group()
            else:
                choice.add_choice(self.parse_choice(line, nesting))


            idx = eol + 1
            eol = block.find('\n', idx+1)
            if eol == -1:
                eol = len(block)

            # print(choice)

        # Skip extra blank line after each block
        self.line_num += 1

        return choice
            # print(choice)

    def parse_choice(self, line, nesting):
        assert re.match('\d+(?: |$)', line), f'{self.current_file} line {self.line_num}: Choice "{line}" must begin with an integer weight!'
        weight_end = line.find(' ')
        if weight_end == -1:
            weight_end = len(line)
        weight = int(line[:weight_end])
        value = line[weight_end+1:]
        sections = value.split('$')
        is_simple = line.find('$') == -1
        return Choice(weight, sections, nesting, is_simple)

    def parse_name(self, data):
        assert data.find('\n'), f'line {self.line_num}: Expected list name at start of file on its own line.'
        eol = data.find('\n')
        name = data[:eol]
        print(f'Name: {name}')
        return data[eol+1:]

    def parse_imports(self, data):
        assert data.find('\n\n'), f'{self.current_file} line {self.line_num}: Expected blank line after name and imports.'
        imports = {}
        eol = data.find('\n')
        line = data[:eol]
        self.line_num += 1
        while line != '':
            # print(f'Import: {line}')
            _import = self.parse_import(line)
            imports[_import[0]] = _import[1]
            new_eol = data.find('\n', eol+1)
            line = data[eol+1:new_eol]
            self.line_num += 1
            eol = new_eol
        return imports, data[eol+1:]

    def parse_import(self, _import):
        assert ':' in _import, f'{self.current_file} line {self.line_num}: Import {_import} does not contain a colon.'
        name, filename = _import.split(':')
        assert re.match(r'[a-zA-Z]\w*', name), f'{self.current_file} line {self.line_num}: Import name {name} does not match pattern of a-zA-Z_.'
        return name, self.parse_file(filename)

    def parse_blocks(self, data):
        if self.current_file == 'shop_test.rg2':
            # data = data.replace(' ', '~')
            print(f'Processed data: {data}')
        blocks = data.split('\n\n')
        # strip empty line in case of file ending with no newline
        blocks[-1] = blocks[-1].rstrip('\n')
        # print(blocks[-1])
        if self.current_file == 'shop_test.rg2':
            print(f'Blocks: {blocks}')
        return blocks

    def preprocess_data(self, data):
        lines = data.split('\n')
        if self.current_file == 'shop_test.rg2':
            print(f'Processed lines: {lines}')
        stripped_lines = [l.rstrip(' ') for l in lines]
        no_trailing_spaces = '\n'.join(stripped_lines)
        # if self.current_file == 'shop_test.rg2':
        #     print(f'Processed data: {no_trailing_spaces}')
        return no_trailing_spaces


def get_nesting(line):
    num_spaces = len(line) - len(line.lstrip(' '))
    return num_spaces // 2
