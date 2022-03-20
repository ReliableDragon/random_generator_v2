

class Expression():

    def __init__(self, clauses=None):
        self.clauses = clauses
        if not self.clauses:
            self.clauses = []
