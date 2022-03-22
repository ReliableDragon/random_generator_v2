import unittest
import logging
import os
import random

logging.basicConfig(format='> %(filename)s:%(lineno)d %(message)s', level=logging.INFO)

from parser import Parser
from generator import Generator
from choice_parser import ChoiceParser
from equation_parser import EquationParser
from subchoice_counter import SubchoiceCounter

class GeneratorTest(unittest.TestCase):

    def test_double_import(self):
        filename = r'test_data\double_import_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_equation_multigen_nested(self):
        filename = r'test_data\equation_multigen_nested_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_equation_weight(self):
        filename = r'test_data\equation_weight_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_function(self):
        filename = r'test_data\function_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_multi_block(self):
        filename = r'test_data\multi_block_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_multi_choice(self):
        filename = r'test_data\multi_choice_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_nested_choices(self):
        filename = r'test_data\nested_choices_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_multi_equation(self):
        filename = r'test_data\multi_equation_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_nested_imports(self):
        filename = r'test_data\nested_imports_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_parens_equation(self):
        filename = r'test_data\parens_equation_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_reordering(self):
        filename = r'test_data\reordering_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_simple_equation(self):
        filename = r'test_data\simple_equation_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_shuffle(self):
        filename = r'test_data\shuffle_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_simple_imports(self):
        filename = r'test_data\simple_imports_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

    def test_simple(self):
        filename = r'test_data\simple_test.rg2'
        result, expected = process_file(filename)
        self.assertEqual(result, expected)

def process_file(filename, override_file = True):
    random.seed(0)
    curr_path = os.getcwd()
    filepath = os.path.join(curr_path, filename)
    dir_path = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    parser = Parser(dir_path)
    choice_blocks, imports = parser.parse_file(filename)
    generator = Generator(choice_blocks, imports)
    result = generator.generate()

    if override_file:
        out_filename = filename + '.gen.out'
        f = open(os.path.join(dir_path, out_filename), mode='w')
        f.write(str(result))
        f.close()

    out_filename = filename + '.gen.out'
    f = open(os.path.join(dir_path, out_filename))
    expected = f.read()
    f.close()

    return str(result), expected
