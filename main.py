import sys
from random import randrange


class Node:

    def __init__(self, id, data):
        self.id = id
        self.data = data

        if id is None:
            self.id = randrange(int(1e9))

    def __str__(self):
        res = ""

        for row in self.data:
            res += str(row)
            res += '\n'

        return res[:-1]


def main(argv):
    mynode = Node(None, [[1, 2, 3], [4, 5, 6]])
    print(mynode)


if __name__ == "__main__":
    main(sys.argv)
