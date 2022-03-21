

class AssignmentParser():

    def __init__(self, parse_var_or_func, num_subchoices, current_file, line_num):
        self.parse_var_or_func = parse_var_or_func
        self.num_subchoices = num_subchoices
        self.current_file = current_file
        self.line_num = line_num

    def parse_assignment(self, line):
        raise NotImplementedError()
        order = 'NONE'
        open_brace = 0
        close_brace = find_matching_brace('[', ']', 0, line)
        expr_start = open_brace + 1
        expr_end = close_brace - 1
        expr_str = line[expr_start:expr_end+1]

        if re.match(r'\d+', expr_str):
            order = int(expr_str)
            assert line[close_brace+1] == '[', f'{self.current_file} line {self.line_num}: Expression {expr_str} had order override, but did not contain an actual expression following it.'
            open_brace = close_brace+1
            close_brace = find_matching_brace('[', ']', open_brace, line)
            expr_start = open_brace + 1
            expr_end = close_brace - 1
            expr_str = line[expr_start:expr_end+1]

        clause_strs = expr_str.split(';')
        clause_strs = [clause_str.strip() for clause_str in clause_strs]
        clauses = [self.parse_clause(clause_str) for clause_str in clause_strs]
        length = close_brace + 1
        return clauses, length
