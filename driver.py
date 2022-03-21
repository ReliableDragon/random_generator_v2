import sys
import os
import logging

from parser import Parser
from generator import Generator
from random_generator import RandomGenerator

#  (:%(funcName)s)
logging.basicConfig(format='> %(filename)s:%(lineno)d %(message)s', level=logging.INFO)

def run():
    assert len(sys.argv) >= 2, 'Must provide a filepath to parse!'
    filepath = sys.argv[1]

    curr_path = os.getcwd()
    if not filepath.startswith(curr_path):
        filepath = os.join(curr_path, filepath)
    dir_path = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    parser = Parser(dir_path)
    choice_blocks, imports = parser.parse_file(filename)

    generator = Generator(choice_blocks, imports, RandomGenerator())
    generation = generator.generate()
    print('\nResults:')
    for i, g in enumerate(generation):
        print(f'{i+1}: {g}')

if __name__ == '__main__':
    run()
