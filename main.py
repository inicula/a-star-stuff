import sys
import copy
from random import randrange

src_data = [];
dest_data = [];
found = False

# utils

def get_bitfields(n):
        res = [];

        for bitfield in range(1, (2**n) - 1):
                remaining = [];

                for pos in range(0, n):
                        mask = 1 << pos;

                        if (~bitfield) & mask:
                                remaining.append(pos);

                res.append(remaining);

        return res;

def popcount(x):
        return bin(x).count("1");

def print_path(path, prefix = None):
        global found;

        found = True

        if prefix is not None:
                print(prefix);

        for i, node in enumerate(path):
                print("{})\n{}\n".format(i + 1, node));
# utils


class Node:
        def __init__(self, id, data):
                self.id = id;
                self.data = data;

                if id is None:
                        self.id = randrange(int(1e9));

        def __eq__(self, other):
                return self.data == other.data;

        def __str__(self):
                res = "";

                for row in self.data:
                        res += str(row);
                        res += '\n';

                return res[:-1];

        def neighbours(self):
                n = len(self.data);
                m = len(self.data[0]);

                res = [];

                # cut columns
                for remaining in get_bitfields(m):

                        new_data = [];
                        for i in range(0, n):
                                line = "";

                                for j in remaining:
                                        line += self.data[i][j];

                                new_data.append(line);

                        res.append(Node(None, new_data));

                # cut rows
                for remaining in get_bitfields(n):
                        new_data = [];

                        for i in remaining:
                                new_data.append(self.data[i]);

                        res.append(Node(None, new_data));

                return res;


def bfs():
        src  = Node(None, src_data);
        dest = Node(None, dest_data);

        q = [[src]];
        while len(q) > 0:
                path_u = q.pop(0);
                u = path_u[len(path_u) - 1];

                if u == dest:
                        print_path(path_u, "[ PATH ]");
                        continue;

                for v in u.neighbours():
                        if v in path_u:
                                continue;

                        new_path = copy.deepcopy(path_u);
                        new_path.append(v);
                        q.append(new_path);

def dfs():
        src  = Node(None, src_data);
        dest = Node(None, dest_data);

        dfs_impl([src], dest);

def dfs_impl(path_so_far, dest):
        u = path_so_far[len(path_so_far) - 1];

        if u == dest:
                print_path(path_so_far, "[ PATH ]")
                return;

        for v in u.neighbours():
                if v in path_so_far:
                        continue;

                path_so_far.append(v);
                dfs_impl(path_so_far, dest);
                path_so_far.pop();


def dfs_iterative():
        src  = Node(None, src_data);
        dest = Node(None, dest_data);

        stack = [[src]];
        while len(stack) > 0:
                path_u = stack.pop();
                u = path_u[len(path_u) - 1];

                if u == dest:
                        print_path(path_u, "[ PATH ]");
                        continue;

                for v in u.neighbours():
                        if v in path_u:
                            continue;

                        new_path = copy.deepcopy(path_u);
                        new_path.append(v);
                        stack.append(new_path);


def main(argv):
        if len(argv) < 2:
                print("Error: argc < 2");
                exit(1);

        global src_data;
        global dest_data;
        global found;

        # read file into string
        filename = argv[1];
        file = open(filename, "r");
        lines = file.readlines();
        lines = [line[:-1] for line in lines];
        file.close();

        # get source and destination from input
        i = 0;
        for _ in range(0, len(lines)):
                if lines[i] == "":
                        i += 1;
                        break;

                src_data.append(lines[i]);
                i += 1;

        for j in range(i, len(lines)):
                dest_data.append(lines[j]);

        # choose handler based on command-line argument
        handlers = {
                "bfs"           : bfs,
                "dfs"           : dfs,
                "dfs_iterative" : dfs_iterative
        };

        method = None;

        try:
                method = handlers[argv[2]];
        except:
                method = dfs_iterative;

        # call the chosen search method
        method();

        if not found:
                print("No path from source to destination was found");


if __name__ == "__main__":
        main(sys.argv);
