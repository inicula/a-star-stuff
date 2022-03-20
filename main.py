import sys
import copy
from random import randrange


def get_bitfields(n):
        res = []

        for bitfield in range(1, (2**n) - 1):
                remaining = []

                for pos in range(0, n):
                        mask = 1 << pos

                        if (~bitfield) & mask:
                                remaining.append(pos)

                res.append(remaining)

        return res


src_data = []
dest_data = []


class Node:
        def __init__(self, id, data):
                self.id = id
                self.data = data

                if id is None:
                        self.id = randrange(int(1e9))

        def __eq__(self, other):
                return self.data == other.data

        def __str__(self):
                res = ""

                for row in self.data:
                        res += str(row)
                        res += '\n'

                return res[:-1]

        def neighbours(self):
                n = len(self.data)
                m = len(self.data[0])

                res = []

                # cut columns
                for remaining in get_bitfields(m):

                        new_data = []
                        for i in range(0, n):
                                line = ""

                                for j in remaining:
                                        line += self.data[i][j]

                                new_data.append(line)

                        res.append(Node(None, new_data))

                # cut rows
                for remaining in get_bitfields(n):
                        new_data = []

                        for i in remaining:
                                new_data.append(self.data[i])

                        res.append(Node(None, new_data))

                return res


def bfs():
        src = Node(None, src_data)
        dest = Node(None, dest_data)

        q = [[src]]

        while len(q) > 0:
                path_u = q.pop(0)
                u = path_u[len(path_u) - 1]

                if u == dest:
                        for node in path_u:
                                print(node, '\n')
                        break

                for v in u.neighbours():
                        if v in path_u:
                                continue

                        new_path = copy.deepcopy(path_u)
                        new_path.append(v)
                        q.append(new_path)


def main(argv):
        if len(argv) != 2:
                print("Error: argc != 2")
                exit(1)

        filename = argv[1]
        file = open(filename, "r")
        lines = file.readlines()
        lines = [line[:-1] for line in lines]
        file.close()

        global src
        global dest

        i = 0
        for _ in range(0, len(lines)):
                if lines[i] == "":
                        i += 1
                        break

                src_data.append(lines[i])
                i += 1

        for j in range(i, len(lines)):
                dest_data.append(lines[j])

        bfs()


if __name__ == "__main__":
        main(sys.argv)
