import random
import logging

logger = logging.getLogger('function')

class Function():

    def __init__(self, name, args):
        self.name = name.lower()
        # logging.info(f'args: {args}')
        self.args = [int(arg) for arg in args]

    def validate(self):
        if self.name == 'gauss':
            if len(self.args) != 2:
                return f'gauss(mu, sigma) function requires exactly 2 parameters, but got {len(self.args)}.'
        elif self.name == 'gamma':
            if len(self.args) != 2:
                return f'gamma(alpha, beta) function requires exactly 2 parameters, but got {len(self.args)}.'
        elif self.name == 'rand':
            if len(self.args) != 2:
                return f'rand(start, stop) function requires exactly 2 parameters, but got {len(self.args)}.'
        elif len(self.args) != 1:
            return f'Dynamic function "{self.name}", interpreted as import, requires exactly 1 parameter, but got {len(self.args)}.'
        else:
            return None

    def execute(self):
        x = self.args[0]
        y = self.args[1]
        if self.name == 'gauss':
            value = random.gauss(x, y)
        elif self.name == 'gamma':
            value = random.gammavariate(x, y)
        elif self.name == 'rand':
            value = random.randint(x, y)
        return str(int(value))

    def __str__(self):
        return f'Function[name: {self.name}, args: {self.args}]'

    def __repr__(self):
        return self.__str__()
