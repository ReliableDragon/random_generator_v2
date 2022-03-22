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
        if self.name in ['gauss', 'gamma', 'rand', 'max', 'min']:
            if len(self.args) != 2:
                return math_error_msg(self.name, self.args)
        # if self.name == 'gauss':
        #     if len(self.args) != 2:
        #         return f'gauss(mu, sigma) function requires exactly 2 parameters, but got {len(self.args)}.'
        # elif self.name == 'gamma':
        #     if len(self.args) != 2:
        #         return f'gamma(alpha, beta) function requires exactly 2 parameters, but got {len(self.args)}.'
        # elif self.name == 'rand':
        #     if len(self.args) != 2:
        #         return f'rand(start, stop) function requires exactly 2 parameters, but got {len(self.args)}.'
        elif self.name == 'shuffle':
            return None
        elif self.name == '$':
            if len(self.args) not in [1, 2, 3]:
                return f'$(choice_group, repetition?, uniqueness_level?) function requires 1 to 3 parameters, but got {len(self.args)}.'
        elif self.name == 'vals':
            if len(self.args) != 1:
                return f'vals(list_to_filter) function requires exactly 1 parameter, but got {len(self.args)}.'
        elif self.name == 'int':
            if len(self.args) != 1:
                return f'int(value) function requires exactly 1 parameter, but got {len(self.args)}.'
        elif self.name == 'rep':
            if len(self.args) not in [4, 5]:
                return f'rep(first, repeated, last_repeated?, last, values) function requires 4 or 5 parameters, but got {len(self.args)}.'
        elif len(self.args) != 1:
            return f'Dynamic function "{self.name}", interpreted as import, requires exactly 1 parameter, but got {len(self.args)}.'
        else:
            return None

    def execute(self, imports, state, generate_import, choice_groups, evaluate_fragment, pick_choice):
        # logger.info(f'Executing function {self}.')
        # logger.info(f'Choice groups: {choice_groups}')
        if self.name in ['gauss', 'gamma', 'rand', 'max', 'min']:
            x = self.args[0]
            y = self.args[1]
            if self.name == 'gauss':
                value = int(random.gauss(int(x), int(y)))
            elif self.name == 'gamma':
                value = int(random.gammavariate(int(x), int(y)))
            elif self.name == 'rand':
                value = int(random.randint(int(x), int(y)))
            elif self.name == 'max':
                value = int(max(int(x), int(y)))
            elif self.name == 'min':
                value = int(min(int(x), int(y)))
        elif self.name == 'shuffle':
            random.shuffle(self.args)
            value = self.args
        elif self.name == 'int':
            value = int(self.args[0])
        # For uniqueness, add another arg here, then filter choice groups.
        elif self.name == '$':
            cg_index = int(self.args[0])
            repetition = 1
            uniqueness = None
            if len(self.args) >= 2:
                repetition = int(self.args[1])
            if len(self.args) >= 3:
                # How many levels deep to make each call unique. 0 is top-level,
                # 1 is the level below, etc. -1 is special, and means "leaf" or
                # no two can be identical. This is destructive, but since choice
                # groups cannot be reused, it should be okay. If that ever changes
                # then this may become a problem. (But you can always just put
                # a choice group into another file and import it if you need to
                # reference it multiple times...)
                uniqueness = int(self.args[2])
            value = []
            # for _ in range(repetition):
            value = pick_choice(choice_groups[cg_index], evaluate_fragment, n=repetition, uniqueness=uniqueness)
            logger.info(f'$-value: {value} of type {type(value)}')
        elif self.name == 'vals':
            lst = self.args[0]
            lst_t = type(lst)
            assert lst_t == list, f'Got function call to vals(list_to_filter), but argument "{lst}", was of type {lst_t}, not list.'
            value = [l for l in lst if l]
        elif self.name == 'rep':
            value = self.build_rep_value()
        elif function.name in self.imports:
            assert len(function.args) == 1, f'Got function call to import "{function.name}", but call did not provide exactly 1 argument.'
            value = generate_import(function.name, function.args[0])
        elif function.name in self.state:
            assert len(function.args) == 1, f'Got function call to reference state "{function.name}", but call did not provide exactly 1 argument.'
            try:
                value = state[function.name][function.args[0]]
            except IndexError:
                value = ''
        else:
            logger.warning(f'Function {function.name} ran, but didn\'t align with any existing function or import!')
            value = ''


        return value

    def build_rep_value(self):
        logger.info(f'rep() called with args: {self.args}')
        # rep("$", ", $", ", and $.", "effects")
        first = None
        repeated = None
        last_repeated = None
        last = None
        values = None
        if len(self.args) == 4:
            first, repeated, last, values = self.args
        elif len(self.args) == 5:
            first, repeated, last_repeated, last, values = self.args
        result = ''
        last_val = len(values) - 1
        # logger.info(f'values: {values}, last_val: {last_val}')
        for i, v in enumerate(values):
            if i == 0:
                result += first.replace('$', v)
            elif i > 0 and i < last_val - 1:
                result += repeated.replace('$', v)
            elif i > 0 and i == last_val - 1:
                if last_repeated:
                    result += last_repeated.replace('$', v)
                else:
                    result += repeated.replace('$', v)
            elif i == last_val:
                result += last.replace('$', v)
            else:
                raise ValueError('Got impossible index!')
        logger.info(f'Result: {result}')
        return result

    def __str__(self):
        return f'Function[name: {self.name}, args: {self.args}]'

    def __repr__(self):
        return self.__str__()

def math_error_msg(name, args, a='a', b='b'):
    return f'{name}({a}, {b}) function requires exactly 2 parameters, but got {len(args)}.'
