

class Expression():

    def __init__(self, clauses=None):
        self.clauses = clauses
        if not self.clauses:
            self.clauses = []

    def evaluate(self, evaluate_fragment):
        result = ''
        for clause in self.clauses:
            clause_result = evaluate_fragment(clause)
            if clause_result:
                result += clause_result
        return result

    def __str__(self):
        s = 'Expression['
        if len(self.clauses) > 0:
            s += str(self.clauses[0])
        for clause in self.clauses[1:]:
            s += f', {str(clause)}'
        return s

    def __repr__(self):
        return self.__str__()
