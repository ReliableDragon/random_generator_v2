import re

from constants import VARIABLE_REGEX, RESERVED_WORDS

class ImportParser():

    def __init__(self, current_file, line_num):
        self.current_file = current_file
        self.line_num = line_num

    def parse_imports(self, data, parse_file_fn):

        if data[0] == '\n':
            # logger.info(f'No imports found, short circuiting imports for {self.current_file}.')
            # No imports, we're currently on the blank line. Consume it and return.
            return {}, data[1:], self.line_num
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
            name, _import = self.parse_import(line, parse_file_fn)
            imports[name] = _import

            new_eol = data.find('\n', eol+1)
            line = data[eol+1:new_eol]
            eol = new_eol
            self.line_num += 1
        # +2 to skip the newlines. Note we're already on the 2nd newline, to be > import_block_end.
        post_import_data = data[eol+1:]
        # logger.info(f'Post import data: {post_import_data}')
        # logger.info(f'Imports: {imports}')
        return imports, post_import_data, self.line_num

    def parse_import(self, import_line, parse_file_fn):
        # logger.info(f'importing: {import_line}')
        assert ':' in import_line, f'{self.current_file} line {self.line_num}: Import {import_line} does not contain a colon.'
        name, filename = import_line.split(':')

        assert name not in RESERVED_WORDS, f'{self.current_file} line {self.line_num}: {name} is a reserved word, and cannot be used as an import name.'
        assert re.match(VARIABLE_REGEX, name), f'{self.current_file} line {self.line_num}: Import name {name} does not match pattern of a-zA-Z_.'

        # Save line_num while we recurse.
        line_num = self.line_num
        _import = parse_file_fn(filename)
        self.line_num = line_num
        return name, _import
