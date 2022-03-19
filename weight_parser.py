import re

class WeightParser():

    def __init__(self, current_file, line_num):
        self.current_file = current_file
        self.line_num = line_num

    def parse_weight(self, line):
        weight_type = self.get_weight_type(line)
        assert weight_type != "INVALID", f'{self.current_file} line {self.line_num}: Choice "{line}" must begin with a valid weight!'
        if weight_type == "NUMERIC":
            re_result = re.match(r'\d+', line)
            end_idx = re_result.end()
            weight = int(line[:end_idx])
            remainder = line[end_idx+1:]
            # Gotta check remainder because a weight-only line is valid.
            while remainder and remainder[0] == ' ':
                remainder = remainder[1:]
            return weight, weight_type, remainder

    def get_weight_type(self, line):
        # Number followed by space
        if re.match(r'\d+ ', line):
            return "NUMERIC"
        # Number on empty line
        elif re.match(r'\d+$', line):
            return "NUMERIC"
        return "INVALID"
