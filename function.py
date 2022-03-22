import random
import logging

from choice_fragment import ChoiceFragment

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
        if self.name in ['gauss', 'gamma', 'beta', 'rand', 'max', 'min']:
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
            return self.validate_rep()
        elif len(self.args) != 1:
            return f'Dynamic function "{self.name}", interpreted as import, requires exactly 1 parameter, but got {len(self.args)}.'
        else:
            return None

    def execute(self, imports, state, generate_import, choice_groups, evaluate_fragment, pick_choice):
        # logger.info(f'Executing function {self}.')
        # logger.info(f'Choice groups: {choice_groups}')
        if self.name in ['gauss', 'gamma', 'beta', 'rand', 'max', 'min']:
            x = self.args[0]
            y = self.args[1]
            if self.name == 'gauss':
                value = int(random.gauss(float(x), float(y)))
            elif self.name == 'gamma':
                value = int(random.gammavariate(float(x), float(y)))
            elif self.name == 'beta':
                value = int(random.betavariate(float(x), float(y)))
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
            # logger.info(f'$() called with args: {self.args}')
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
            # logger.info(f'$-value: {value} of type {type(value)}')
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
        last_repeated = ''
        last = None
        values = []

        if type(self.args[3]) == list:
        # if len(self.args) == 4:
            first, repeated, last = self.args[:3]
            idx = 3
        # elif len(self.args) == 5:
        else:
            first, repeated, last_repeated, last = self.args[:4]
            idx = 4
        values = self.args[idx:]

        result = ''
        # logger.info(f'values: {values}, last_val: {last_val}')
        last_val = len(values[0]) - 1
        for i in range(len(values[0])):
            if i == 0:
                first_edit = first
                for v in values:
                    first_edit = first_edit.replace('$', v[i], 1)
                result += first_edit
            elif i > 0 and i < last_val - 1:
                repeated_edit = repeated
                for v in values:
                    repeated_edit = repeated_edit.replace('$', v[i], 1)
                result += repeated_edit
            elif i > 0 and i == last_val - 1:
                if last_repeated:
                    last_repeated_edit = last_repeated
                    for v in values:
                        last_repeated_edit = last_repeated_edit.replace('$', v[i], 1)
                    result += last_repeated_edit
                else:
                    repeated_edit = repeated
                    for v in values:
                        repeated_edit = repeated_edit.replace('$', v[i], 1)
                    result += repeated_edit
            elif i == last_val:
                last_edit = last
                for v in values:
                    last_edit = last_edit.replace('$', v[i], 1)
                result += last_edit
            else:
                raise ValueError('Got impossible index!')

        return result

    def validate_rep(self):
        if len(self.args) < 4:
            return f'rep(first, repeated, last_repeated?, last, values...) function at least 4 parameters, but got {len(self.args)}.'

        d = self.args[3]
        choice_vals = [a for a in self.args if type(a) == ChoiceFragment and a.type == 'TEXT']
        logger.info(f'choice_vals: {choice_vals}')
        num_strs = 4 if type(d) == ChoiceFragment and d.type == 'TEXT' else 3
        if not (len(choice_vals) in [3, 4] and all(map(lambda a: a.type == 'TEXT', self.args[:num_strs]))):
        # if not (ta == tb == tc == td == str or (ta == tb == tc == str and td == list)):
            return f'rep(first, repeated, last_repeated?, last, values...) function takes text for the non-values parameters, but got {self.args}.'

        for arg in self.args[num_strs:]:
            if not type(arg) == ChoiceFragment and arg.value == 'VARIABLE':
                return f'rep(first, repeated, last_repeated?, last, values...) function takes variables for the values parameters, but got {type(arg)} for one of them instead in args {self.args}.'

        for cv in choice_vals:
            logger.info(f'self.args: {self.args}')
            logger.info(f'cv: {cv}')
            logger.info(f'num_strs: {num_strs}')
            if not cv.value.count('$') == len(self.args) - num_strs:
                return f'rep(first, repeated, last_repeated?, last, values...) function requires the same number of $ in each non-values argument as there are variables passed to values. Instead, we saw {self.args}.'
        return None

    def __str__(self):
        return f'Function[name: {self.name}, args: {self.args}]'

    def __repr__(self):
        return self.__str__()

def math_error_msg(name, args, a='a', b='b'):
    return f'{name}({a}, {b}) function requires exactly 2 parameters, but got {len(args)}.'
