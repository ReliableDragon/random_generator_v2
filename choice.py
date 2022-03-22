from choice_group import ChoiceGroup

class Choice():

    def __init__(self, weight, fragments, level):
        self.weight = weight
        self.fragments = fragments
        self.nesting = level
        self.level = level
        self.choice_groups = []

    def add_choice(self, choice):
        if not self.choice_groups:
            self.choice_groups.append(ChoiceGroup(self.level, self.nesting))
        self.choice_groups[-1].add_choice(choice)

    def add_choice_group(self):
        if self.level == self.nesting - 1:
            self.choice_groups.append(ChoiceGroup(self.level, self.nesting))
        else:
            self.choice_groups[-1].add_choice_group()

    def set_nesting(self, nesting):
        self.nesting = nesting
        if self.choice_groups:
            self.choice_groups[-1].set_nesting(nesting)

    def make_str(self):
        s = f'\n{" " * (2 * self.level)}Choice[weight: {self.weight}, fragments: {"".join(str(self.fragments))}, level: {self.level}, nesting: {self.nesting}]\n'
        s += f'{" " * (2 * self.level)}{self.weight}: {"".join([str(f.value) for f in self.fragments])}'
        for i, choice_group in enumerate(self.choice_groups):
            s += choice_group.make_str()
            if i != len(self.choice_groups) - 1:
                s += '\n$'
        return s

    def __str__(self):
        return self.make_str()

    def __repr__(self):
        return self.__str__()
