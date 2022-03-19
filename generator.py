import random
import math
import logging

from heapq import heappush, heappop
from itertools import zip_longest

logger = logging.getLogger('generator')

class Generator():

    def __init__(self, choice_blocks, imports):
        self.choice_blocks = choice_blocks
        self.imports = imports
        self.state = {}

    def generate(self):
        results = []
        # logging.info(f'Imports: {self.imports}')
        for root_choice in self.choice_blocks:
            logger.info(f'Root choice: {root_choice}')
            # Have to do the first roll out here, because technically the root choices are equivalent to choice blocks,
            # since there's no line to use as a choice.
            self.state = {}
            choice = self.pick_choice(root_choice)
            # TODO: Consider if having persistent state for whole file would be worthwhile.
            results.append(choice)
        # logging.info(f'Results: {results}')
        return results

    def generate_choice(self, choice):
        ordered_fragments = []
        values = []
        choice_groups = choice.choice_groups
        logging.info(f'Unordered fragments: {choice.fragments}')
        for i, fragment in enumerate(choice.fragments):
            order = fragment.order
            if order == 'NONE':
                order = math.inf
            heappush(ordered_fragments, (order, i, fragment))
        logging.info(f'Ordered fragments: {ordered_fragments}')
        for _, i, fragment in ordered_fragments:
            value = self.evaluate_fragment(fragment, choice)
            heappush(values, (i, value))

        # logging.info(f'values: {values}')
        result = ''.join([value for i, value in values])
        # logger.info(f'result: {result}')
        return result

    def evaluate_fragment(self, fragment, choice):
        logging.info(f'Fragment: {fragment}')
        if fragment.type == 'TEXT':
            return fragment.value

        if fragment.type == 'SUBCHOICE':
            choice_group = choice.choice_groups[fragment.value]
            return self.pick_choice(choice_group)

        if fragment.type == 'VARIABLE':
            variable = fragment.value
            return self.generate_variable(variable)

        if fragment.type == 'FUNCTION':
            logger.info(f'Function fragment: {fragment}')
            function = fragment.value
            function.args = [self.evaluate_fragment(f, choice) for f in function.args]
            if function.name in self.imports:
                assert len(function.args) == 1, f'Got function call to import "{function.name}", but call did not provide exactly 1 argument.'
                return self.generate_import(function.name, function.args[0])
            return str(function.execute())

        if fragment.type == 'EXPRESSION':
            logger.info(f'Expression fragment: {fragment}')
            expression = fragment.value
            value, self.state = expression.evaluate(choice, self.state)
            return str(value)


    def generate_variable(self, variable):
        logging.info(f'Evaluating variable {variable}')
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
            result = results[position]
        return result

    def pick_choice(self, choice_group):
        # logger.info(f'Choice Group: {choice_group}')
        # logger.info(choice_group)
        total = sum([c.weight for c in choice_group.choices])
        rand = random.randint(1, total)
        # logger.info(f'total: {total}, rand: {rand}')
        i = -1
        _sum = 0
        # < bc otherwise we'll roll again when at max value and overshoot
        while _sum < rand:
            i += 1
            # logger.info(f'i: {i}, sum: {_sum}, choice weight: {choice_group.choices[i].weight}')
            _sum += choice_group.choices[i].weight
        chosen = choice_group.choices[i]
        # logger.info(chosen)
        return self.generate_choice(chosen)
