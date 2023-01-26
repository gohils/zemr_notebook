"The Iterator Pattern Concept"


class NumberWheel():  # pylint: disable=too-few-public-methods
    "The concrete iterator (iterable)"

    def __init__(self):
        self.index = 0

    def next(self):
        """Return a new number next in the wheel"""
        self.index = self.index + 1
        return self.index * 2 % 11


# The Client
NUMBERWHEELA = NumberWheel()
NUMBERWHEELB = NumberWheel()

for i in range(5):
    print(NUMBERWHEELA.next(), end=", ")

for i in range(5):
    print(NUMBERWHEELB.next(), end=", ")
