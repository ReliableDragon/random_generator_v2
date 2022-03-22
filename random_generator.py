import random

class RandomGenerator():

    def __init__(self, seed=None):
        self.seed = seed

    def randint(self, a, b):
        return random.randint(a, b)

    
