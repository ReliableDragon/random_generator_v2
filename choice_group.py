import logging

logger = logging.getLogger('choice_group')


class ChoiceGroup():

    def __init__(self, level, nesting):
        self.choices = []
        self.level = level
        self.nesting = nesting

    def add_choice(self, choice):
        # logger.info(f'Nesting: {self.nesting}, Level: {self.level}')
        if self.nesting == self.level + 1:
            self.choices.append(choice)
        else:
            self.choices[-1].add_choice(choice)

    def add_choice_group(self):
        self.choices[-1].add_choice_group()

    def set_nesting(self, nesting):
        self.nesting = nesting
        self.choices[-1].set_nesting(nesting)

    def make_str(self):
        s = f'\n{" " * (2 * self.level)}CG[level: {self.level}, nesting: {self.nesting}]'
        for choice in self.choices:
            s += '\n' + choice.make_str()
        return s

    def __str__(self):
        return self.make_str()

    def __repr__(self):
        return self.__str__()
