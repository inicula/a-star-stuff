import sys
import copy
import stopit
from random import randrange

usage = "usage: python3 main.py --file <filename> [--method <search_method>] [--timeout <timeout_value>]"

max_sols = int(1e9);
sols_found = 0;
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


@stopit.threading_timeoutable(default = "1")
def bfs():
        global sols_found;
        sols_found = 0;

        src  = Node(None, src_data);
        dest = Node(None, dest_data);

        q = [[src]];
        while len(q) > 0:
                path_u = q.pop(0);
                u = path_u[len(path_u) - 1];

                if u == dest:
                        print_path(path_u, "[ PATH ]");

                        sols_found += 1;
                        if sols_found == max_sols:
                                break;

                        continue;

                for v in u.neighbours():
                        if v in path_u:
                                continue;

                        new_path = copy.deepcopy(path_u);
                        new_path.append(v);
                        q.append(new_path);

        return "0";

@stopit.threading_timeoutable(default = "1")
def dfs():
        global sols_found;
        sols_found = 0;

        src  = Node(None, src_data);
        dest = Node(None, dest_data);

        dfs_impl([src], dest);
        return "0";

def dfs_impl(path_so_far, dest):
        global sols_found;

        if sols_found == max_sols:
                return;

        u = path_so_far[len(path_so_far) - 1];

        if u == dest:
                print_path(path_so_far, "[ PATH ]")
                sols_found += 1;
                return;

        for v in u.neighbours():
                if v in path_so_far:
                        continue;

                path_so_far.append(v);
                dfs_impl(path_so_far, dest);
                path_so_far.pop();


@stopit.threading_timeoutable(default = "1")
def dfs_iterative():
        global sols_found;
        sols_found = 0;

        src  = Node(None, src_data);
        dest = Node(None, dest_data);

        stack = [[src]];
        while len(stack) > 0:
                path_u = stack.pop();
                u = path_u[len(path_u) - 1];

                if u == dest:
                        print_path(path_u, "[ PATH ]");

                        sols_found += 1;
                        if sols_found == max_sols:
                                break;

                        continue;

                for v in u.neighbours():
                        if v in path_u:
                            continue;

                        new_path = copy.deepcopy(path_u);
                        new_path.append(v);
                        stack.append(new_path);

        return "0";


def main(argv):
        global src_data;
        global dest_data;
        global found;
        global max_sols;

        argc = len(argv);

        if argc < 2:
                print("Error: not enough cli arguments.")
                print(usage);
                exit(1);

        filename    = "";
        method_arg  = "";
        timeout_sec = 60;
        try:
                for i in range(1, argc):
                        if argv[i] == "--method":
                                method_arg = argv[i + 1];
                                i += 1;

                        if argv[i] == "--timeout":
                                timeout_sec = float(argv[i + 1]);
                                i += 1;

                        if argv[i] == "--file":
                                filename = argv[i + 1];
                                i += 1;

                        if argv[i] == "--stop-after":
                                max_sols = int(argv[i + 1]);
                                i += 1;

                if filename == "":
                        raise Exception('');

        except:
                print("Erorr in cli args.");
                print(usage);
                exit(1);

        # read file into string
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
                method = handlers[method_arg];

        except:
                print(
                    "Method '{}' not found. Picking depth-first search as default.\n".
                    format(method_arg),
                    file = sys.stderr
                );
                method = dfs;

        # call the chosen search method
        res = method(timeout = timeout_sec);

        if res == "1":
                print("The search algorithm was timed out.");
                return;

        if not found:
                print("No path from source to destination was found.");


if __name__ == "__main__":
        main(sys.argv);
