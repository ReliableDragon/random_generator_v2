from choice import Choice

class RootChoice():

    def __init__(self):
        self.choices = []
        self.nesting = 0
        imported_data = {}

    def add_choice(self, choice):
        # print(f'Adding choice {value}:{weight}')
        if self.nesting == 0:
            self.choices.append(choice)
        else:
            self.choices[-1].add_choice(choice)

    def add_choice_group(self):
        # print('Adding choice group')
        self.choices[-1].add_choice_group()

    def set_nesting(self, nesting):
        # print(f'Setting nesting to {nesting}.')
        if nesting != self.nesting:
            self.nesting = nesting
            self.choices[-1].set_nesting(nesting)

    def __str__(self):
        s = '\nChoice Block:'
        for choice in self.choices:
            s += choice.make_str() + '\n'
        return s

    def __repr__(self):
        return self.__str__()
