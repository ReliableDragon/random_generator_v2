import sys

def fix_braces(filename):

    f = open(filename, 'r')
    text = f.read()
    f.close()
    fixed = ''
    indent = 0
    idx = 0
    while idx < len(text):
        # print(idx)
        c = text[idx]
        if c == '[':
            indent += 2
            fixed += c
            fixed += '\n'
            fixed += ' ' * indent
        elif c == ']':
            indent -= 2
            fixed += '\n'
            fixed += ' ' * indent
            fixed += c
        elif c == ',':
            fixed += c
            fixed += '\n'
            fixed += ' ' * indent
            while idx + 1 < len(text) and text[idx+1] == ' ':
                idx += 1
        elif c != '"':
            fixed += c
        idx += 1
    f = open(filename, 'w')
    f.write(fixed)
    f.close()

if __name__ == '__main__':
    assert len(sys.argv) >= 2, 'Must provide a filepath to parse!'
    filename = sys.argv[1]
    fix_braces(filename)
