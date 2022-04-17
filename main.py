import sys
import copy
import stopit
import time
from random import randrange

# global variables
begin_time       = time.time();
max_nodes_in_mem = 0;
calculated_nodes = 0;
max_sols         = int(1e9);
sols_found       = 0;
src_data         = [];
dest_data        = [];
usage            = ("usage: python3 main.py --file <filename> "
                    "[--timeout <timeout_value>] [--stop-after <number_of_solutions>]");
# global variables

# utils
def remaining_after_cut(n):
        res = [];

        for i in range(0, n):
                for j in range(i, n):
                        current = []

                        for k in range(0, i):
                                current.append(k);

                        for k in range(j + 1, n):
                                current.append(k);

                        if len(current) == 0:
                                continue;

                        res.append(current);

        return res;

def popcount(x):
        return bin(x).count("1");

def check_full_rows(mat):
        if len(mat) == 0:
                return False;

        if len(mat[0]) == 0:
                return False;

        n, m = len(mat), len(mat[0]);

        for i in range(n):
            if len(mat[i]) != m:
                    return False;

        return True;

def print_path(path, prefix = None):
        now = time.time();
        dur = now - begin_time;

        if prefix is not None:
                print(prefix);

        for i, node in enumerate(path):
                print("{})\n{}\n".format(i + 1, node));

        print("Solution found after {} seconds".format(dur));

def printerr(*args):
        print(*args, file = sys.stderr);
# utils

class Node:
        def __init__(self, id, data, g = None, heuristic = None):
                self.id = id;
                self.data = data;

                self.g = None
                self.h = None;
                self.f = None;

                if heuristic is not None:
                        self.g = g;
                        self.h = heuristic(self.data);
                        self.f = self.g + self.h;

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
                global calculated_nodes;
                calculated_nodes += 1;

                n = len(self.data);
                m = len(self.data[0]);

                res = [];

                # cut columns
                for remaining in remaining_after_cut(m):

                        new_data = [];
                        for i in range(0, n):
                                line = "";

                                for j in remaining:
                                        line += self.data[i][j];

                                new_data.append(line);

                        res.append(Node(None, new_data));

                # cut rows
                for remaining in remaining_after_cut(n):
                        new_data = [];

                        for i in remaining:
                                new_data.append(copy.deepcopy(self.data[i]));

                        res.append(Node(None, new_data));

                return res;

def check_early(initial_state):
        n1, m1 = len(initial_state), len(initial_state[0]);
        n2, m2 = len(dest_data), len(dest_data[0]);

        return n1 >= n2 and m1 >= m2;

def heuristic_v1(state):
        if state == dest_data:
                return 0;
        return 1;

def heuristic_v2(state):
        n1 = len(state);
        m1 = len(state[0]);

        n2 = len(dest_data);
        m2 = len(dest_data[0]);

        if n2 > n1 or m2 > m1:
                return int(1e9);

        total_cost = 0;

        row_surplus = n1 - n2;
        if row_surplus > 0:
                total_cost += m2 / row_surplus;

        col_surplus = m1 - m2;
        if col_surplus > 0:
                total_cost += 1;

        return total_cost;

@stopit.threading_timeoutable(default = "1")
def bfs():
        global sols_found;
        global max_nodes_in_mem;

        src  = Node(None, src_data);
        dest = Node(None, dest_data);

        q = [[src]];
        while len(q) > 0:
                max_nodes_in_mem = max(max_nodes_in_mem, len(q));

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
        src  = Node(None, src_data);
        dest = Node(None, dest_data);

        dfs_impl([src], dest);
        return "0";

def dfs_impl(path_so_far, dest):
        global sols_found;
        global max_nodes_in_mem;

        max_nodes_in_mem = max(max_nodes_in_mem, len(path_so_far));

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
        global max_nodes_in_mem;

        src  = Node(None, src_data);
        dest = Node(None, dest_data);

        stack = [[src]];
        while len(stack) > 0:
                max_nodes_in_mem = max(max_nodes_in_mem, len(stack));

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
        global max_sols;
        global calculated_nodes;
        global max_nodes_in_mem;
        global sols_found;
        global begin_time;

        argc = len(argv);

        if argc < 2:
                printerr("Error: not enough cli arguments.")
                printerr(usage);
                exit(1);

        filename    = "";
        timeout_sec = 60;
        try:
                for i in range(1, argc):
                        if argv[i] == "--timeout" or argv[i] == "-t":
                                timeout_sec = float(argv[i + 1]);
                                i += 1;

                        if argv[i] == "--file" or argv[i] == "-f":
                                filename = argv[i + 1];
                                i += 1;

                        if argv[i] == "--stop-after" or argv[i] == "-s":
                                max_sols = int(argv[i + 1]);
                                i += 1;

                if filename == "":
                        raise Exception('');

        except:
                printerr("Erorr in cli args.");
                printerr(usage);
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

        # check input validity
        if not (check_full_rows(src_data) and check_full_rows(dest_data)):
                printerr("Invalid input.");
                return;

        # check if solutions are possible
        if not check_early(src_data):
                print("No solutions possible for any search algorithm.");
                return;

        # choose handler based on command-line argument
        methods = [
                ("bfs",           bfs),
                ("dfs",           dfs),
                ("dfs_iterative", dfs_iterative)
        ];

        # search with all methods
        for mname, mfunc in methods:
                print("Searching with algorithm: {}\n".format(mname));

                # reset global state
                max_nodes_in_mem = 0;
                calculated_nodes = 0;
                sols_found = 0;
                begin_time = time.time();

                # apply search algorithm
                res = mfunc(timeout = timeout_sec);

                if res == "1":
                        print("The search algorithm was timed out.");

                if sols_found == 0:
                        print("No path from source to destination was found.");

                print("Max nodes in memory: {}".format(max_nodes_in_mem));
                print("Expanded nodes: {}\n".format(calculated_nodes));


if __name__ == "__main__":
        main(sys.argv);
