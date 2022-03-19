import random

from itertools import zip_longest

class Generator():

    def __init__(self, choice_blocks):
        self.choice_blocks = choice_blocks

    def generate(self):
        results = []
        for root_choice in self.choice_blocks:
            choice = self.pick_choice(root_choice)
            results.append(self.generate_choice(choice))
        return results

    def generate_choice(self, choice):
        choices = []
        for choice_group, section in zip(choice.choice_groups, choice.sections):
            chosen = self.pick_choice(choice_group)

            if chosen.is_simple:
                print(f'Simple choice chosen.')
                choices.append(chosen.sections[0])
            else:
                print('Nested choice chosen.')
                choices.append(self.generate_choice(chosen))

        result = ''.join(map(''.join, zip_longest(choice.sections, choices, fillvalue='')))
        return result


    def pick_choice(self, choice_group):
        # print(choice_group)
        total = sum([c.weight for c in choice_group.choices])
        rand = random.randint(1, total)
        # print(f'total: {total}, rand: {rand}')
        i = -1
        _sum = 0
        # < bc otherwise we'll roll again when at max value and overshoot
        while _sum < rand:
            i += 1
            # print(f'i: {i}, sum: {_sum}, choice weight: {choice_group.choices[i].weight}')
            _sum += choice_group.choices[i].weight
        chosen = choice_group.choices[i]
        # print(chosen)
        return chosen
