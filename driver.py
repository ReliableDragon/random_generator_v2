import sys
import os
import logging

from parser import Parser
from generator import Generator

#  (:%(funcName)s)
logging.basicConfig(format='> %(filename)s:%(lineno)d %(message)s', level=logging.INFO)

def run():
    assert len(sys.argv) >= 2, 'Must provide a filename to parse!'
    filename = sys.argv[1]

    parser = Parser(os.path.dirname(filename))
    choice_blocks, imports = parser.parse_file(os.path.basename(filename))

    generator = Generator(choice_blocks, imports)
    generation = generator.generate()
    print('\nResults:')
    for i, g in enumerate(generation):
        print(f'{i+1}: {g}')

if __name__ == '__main__':
    run()
