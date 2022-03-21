
def fix_braces(filename):
    f = open(filename, 'r')
    text = f.read()
    f.close()
    fixed = ''
    indent = 0
    for c in text:
        if c in ['"', ' ']:
            continue
        elif c == '[':
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
        else:
            fixed += c
    f = open(filename, 'w')
    f.write(fixed)
    f.close()
