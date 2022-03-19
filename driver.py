import sys
import os

from parser import Parser
from generator import Generator

def run():
    assert len(sys.argv) >= 2, 'Must provide a filename to parse!'
    filename = sys.argv[1]

    parser = Parser(os.path.dirname(filename))
    choice_blocks = parser.parse_file(os.path.basename(filename))

    generator = Generator(choice_blocks)
    generation = generator.generate()
    print(generation)

if __name__ == '__main__':
    run()
