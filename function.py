import random
import logging

logger = logging.getLogger('function')

# TODO: Consider making the args fragments, and having the generator evaluate them,
# so that we can do fun stuff, e.g., a randomize() function that can randomly order
# the results of other calls.
class Function():

    def __init__(self, name, args):
        self.name = name.lower()
        # logging.info(f'args: {args}')
        self.args = args

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
        elif self.name == 'shuffle':
            return None
        elif len(self.args) != 1:
            return f'Dynamic function "{self.name}", interpreted as import, requires exactly 1 parameter, but got {len(self.args)}.'
        else:
            return None

    def execute(self, imports, generate_import):
        x = self.args[0]
        y = self.args[1]
        if self.name == 'gauss':
            value = int(random.gauss(int(x), int(y)))
        elif self.name == 'gamma':
            value = int(random.gammavariate(int(x), int(y)))
        elif self.name == 'rand':
            value = int(random.randint(int(x), int(y)))
        elif self.name == 'shuffle':
            random.shuffle(self.args)
            value = self.args
        elif function.name in self.imports:
            assert len(function.args) == 1, f'Got function call to import "{function.name}", but call did not provide exactly 1 argument.'
            value = generate_import(function.name, function.args[0])
        else:
            logger.warning(f'Function {function.name} ran, but didn\'t align with any existing function or import!')
            value = ""


        return value

    def __str__(self):
        return f'Function[name: {self.name}, args: {self.args}]'

    def __repr__(self):
        return self.__str__()
