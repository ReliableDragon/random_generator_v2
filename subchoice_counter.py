

class SubchoiceCounter():

    def __init__(self, count=0):
        self.count = count

    def incr(self):
        self.count += 1

    def decr(self):
        self.count -= 1

    def set(self, val):
        self.count = val
