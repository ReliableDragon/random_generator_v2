import random
import math
import logging

from equation import Equation

from heapq import heappush, heappop
from itertools import zip_longest

logger = logging.getLogger('generator')

class Generator():

    def __init__(self, choice_blocks, imports):
        self.choice_blocks = choice_blocks
        self.imports = imports
        self.chosen = {}
        self.state = {}
        # self.random_generator = random_generator

    def generate(self):
        results = []
        # logging.info(f'Imports: {self.imports}')
        self.state = {}
        for root_choice in self.choice_blocks:
            # logger.info(f'Root choice: {root_choice}')
            curryed_evaluate_fragment = lambda a: self.evaluate_fragment(a, root_choice)
            # Have to do the first roll out here, because technically the root choices are equivalent to choice blocks,
            # since there's no line to use as a choice.
            choice = self.pick_choice(root_choice, curryed_evaluate_fragment)
            # TODO: Consider if having persistent state for whole file would be worthwhile.
            results.append(choice)
        # logging.info(f'Results: {results}')
        return results

    def generate_choice(self, choice, uniqueness = None):
        ordered_fragments = []
        values = []
        choice_groups = choice.choice_groups
        # logging.info(f'Unordered fragments: {choice.fragments}')

        for i, fragment in enumerate(choice.fragments):
            order = fragment.order
            if order == 'NONE':
                order = math.inf
            heappush(ordered_fragments, (order, i, fragment))
        # logging.info(f'Ordered fragments: {ordered_fragments}')

        for _, i, fragment in ordered_fragments:
            value = self.evaluate_fragment(fragment, choice, uniqueness=uniqueness)
            heappush(values, (i, value))

        # logging.info(f'values: {values}')
        result = ''.join([value for i, value in values])
        # logger.info(f'result: {result}')
        return result

    def evaluate_fragment(self, fragment, choice, uniqueness = None):
        # logging.info(f'Fragment: {fragment}')
        curryed_evaluate_fragment = lambda a: self.evaluate_fragment(a, choice, uniqueness=uniqueness)
        if fragment.type == 'TEXT':
            return fragment.value

        if fragment.type == 'SUBCHOICE':
            choice_group = choice.choice_groups[fragment.value]
            return self.pick_choice(choice_group, curryed_evaluate_fragment, uniqueness=uniqueness)

        if fragment.type == 'VARIABLE':
            variable = fragment.value
            return self.generate_variable(variable)

        if fragment.type == 'FUNCTION':
            # logger.info(f'Function fragment: {fragment}')
            function = fragment.value
            function.args = [curryed_evaluate_fragment(f) for f in function.args]
            # logger.info(f'Function post-arg-evaluation: {function}')
            return function.execute(self.imports, self.state, self.generate_import, choice.choice_groups, curryed_evaluate_fragment, self.pick_choice)

        if fragment.type == 'EXPRESSION':
            # logger.info(f'Expression fragment: {fragment}')
            expression = fragment.value
            # logger.info(f'Expression: {expression}')
            value = expression.evaluate(curryed_evaluate_fragment)
            return str(value)

        if fragment.type == 'EQUATION':
            # logger.info(f'Expression fragment: {fragment}')
            expression = fragment.value
            # logger.info(f'Expression: {expression}')
            value = expression.evaluate(curryed_evaluate_fragment)
            return str(value)

        if fragment.type == 'ASSIGNMENT':
            # logger.info(f'Expression fragment: {fragment}')
            expression = fragment.value
            # logger.info(f'Expression: {expression}')
            self.state = expression.evaluate(self.state, curryed_evaluate_fragment)
            return ''


    def generate_variable(self, variable):
        # logging.info(f'Evaluating variable {variable}')
        if variable in self.imports:
            return self.generate_import(variable)
        elif variable in self.state:
            return self.state[variable]
        else:
            logging.warning(f'Got variable not present in imports or state: "{variable}".')
            return ""

    def generate_import(self, variable, position=0):
        # logging.info(f'Imported choice blocks: {self.imports[variable]}')
        import_data, import_imports = self.imports[variable]
        sub_generator = Generator(import_data, import_imports)
        results = sub_generator.generate()
        # Implicitly take the first result when calling as a variable.
        # This is basically sugar for @import(1).
        if not results:
            logging.warning(f'Generated empty results for import variable "{variable}"! Are you sure this is what you wanted?')
            result = ''
        else:
            try:
                result = results[position]
            except IndexError:
                logging.warning(f'Accessed invalid index for import variable "{variable}"! Are you sure this is what you wanted?')
                result = ''
        return result

    def pick_choice(self, choice_group, evaluate_fragment, n=1, uniqueness=None):
        # logger.info(f'Choice Group: {choice_group}')
        # logger.info(choice_group)
        # logger.info(f'Weights: {[c.weight for c in choice_group.choices]}')
        evaluated_weights = []
        for choice in choice_group.choices:
            weight = choice.weight
            if type(weight) == Equation:
                evaluated_weight = weight.evaluate(evaluate_fragment)
                try:
                    weight = int(evaluated_weight)
                except ValueError:
                    logger.fatal(f'Choice {weight} in choice_group {choice_group} evaluated to {evaluated_weight}, which could not be converted to an integer weight.')
                    raise
            evaluated_weights.append(weight)
        # logger.info(f'Evaluated weights: {evaluated_weights}')
        return self.generate_choices(evaluated_weights, choice_group, evaluate_fragment, n, uniqueness)

    def generate_choices(self, weights, choice_group, evaluate_fragment, n=1, uniqueness=None):
        result = []
        total = sum(weights)
        for i in range(n):
            rand = random.randint(1, total)
            # logger.info(f'total: {total}, rand: {rand}')
            i = -1
            _sum = 0
            # < bc otherwise we'll roll again when at max value and overshoot
            while _sum < rand:
                i += 1
                # logger.info(f'i: {i}, sum: {_sum}, choice weight: {choice_group.choices[i].weight}')
                # These are in sync with choice_group.choices, as we don't want to override
                # those, in case we evaluate this choice group multiple times.
                _sum += weights[i]
            chosen = choice_group.choices[i]
            if uniqueness == 0:
                del choice_group.choices[i]
            # logger.info(chosen)
            og_uniqueness = uniqueness
            if uniqueness == 0:
                uniqueness = None
            elif uniqueness != None and uniqueness != -1:
                uniqueness=uniqueness-1
            choice = self.generate_choice(chosen, uniqueness=uniqueness)
            uniqueness = og_uniqueness

            result.append(choice)

        if n == 1:
            result = result[0]
        return result







# keep buffer
