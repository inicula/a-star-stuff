import sys
import copy
import stopit
import time
import heapq
import itertools
import queue

# global variables
output_file      = sys.stdout
begin_time       = time.time()
max_nodes_in_mem = 0
calculated_nodes = 0
max_sols         = int(1e9)
sols_found       = 0
src_data         = []
dest_data        = []
usage            = ("usage: python3 main.py --file <filename> "
                    "[--timeout <timeout_value>] [--stop-after <number_of_solutions>] "
                    "[--output-dir <dir_path>]")

# utils
def mprint(*args):
        print(*args, file=output_file)

def lines_from_file(filename):
        file  = open(filename, "r")
        lines = file.readlines()
        lines = [line[:-1] for line in lines]
        file.close()

        return lines

def mat_size(mat):
        n, m = len(mat), 0
        if n != 0:
                m = len(mat[0])

        return n, m

def reset_global_state():
        # reset global variables before each algorithm

        global max_nodes_in_mem
        global calculated_nodes
        global sols_found
        global begin_time

        max_nodes_in_mem = 0
        calculated_nodes = 0
        sols_found       = 0
        begin_time       = time.time()

def possible_cuts(n):
        # get all non-empty consecutive sequences from [0 ... n - 1]

        res = []
        for i in range(0, n):
                for j in range(i, n):
                        current = list(range(i, j + 1))

                        if len(current) == 0 or len(current) == n:
                                continue

                        res.append(current)

        return res

def remaining_after_cut(cut, n):
        # get remaining rows/columns after applying a cut

        left = list(range(0, cut[0]))
        right = list(range(cut[len(cut) - 1] + 1, n))
        return left + right

def check_full_rows(mat):
        # check matrix representation validity

        n, m = mat_size(mat)
        if n == 0 or m == 0:
                return False

        for i in range(n):
                if len(mat[i]) != m:
                        return False

        return True

def via_rows(rows):
        # get explicit string for a row cut

        return "Eliminated rows: {}".format(", ".join(map(str, rows)))

def via_columns(cols):
        # get explicit string for a column cut

        return "Eliminated columns: {}".format(", ".join(map(str, cols)))

def get_f(path):
        # function for returning the tentative distance from a path sequence

        return path[len(path) - 1].f

def print_path(path, prefix=None):
        # print a path that leads to a goal node and also some of its details

        now = time.time()
        dur = now - begin_time

        if prefix is not None:
                mprint(prefix)

        mprint("{})\n{}\n".format(1, path[0]))
        for i, node in enumerate(path[1:]):
                mprint("{}\n\n{})\n{}\n".format(node.via, i + 2, node))

        mprint("Solution cost: {}".format(path[len(path) - 1].g))
        mprint("Solution found after {:.3f} seconds\n".format(dur))

def print_alg_info(res):
        # print information about an algorithm and its used resources

        if res == "1":
                mprint("The search algorithm was timed out.")

        if sols_found == 0:
                mprint("No path from source to destination was found.")

        mprint("Max nodes in memory: {}".format(max_nodes_in_mem))
        mprint("Expanded nodes: {}\n".format(calculated_nodes))


def printerr(*args):
        # print to standard error

        print(*args, file=sys.stderr)

# Node class and search functions
class Node:
        def __init__(self, data, g, heuristic=None, via=None):
                self.data = data
                self.via = via

                self.g = g
                self.h = None
                self.f = None

                if heuristic is not None:
                        self.h = heuristic(self.data)
                        self.f = self.g + self.h

        def __eq__(self, other):
                return self.data == other.data

        def __lt__(self, other):
                return self.f < other.f

        def __str__(self):
                res = ""

                for row in self.data:
                        res += str(row)
                        res += '\n'

                return res[:-1]

        def neighbours(self, hfunc=None):
                global calculated_nodes
                calculated_nodes += 1

                n, m = mat_size(self.data)

                res = []

                # cut columns
                for pos_cut in possible_cuts(m):
                        remaining = remaining_after_cut(pos_cut, m)

                        new_data = []
                        for i in range(0, n):
                                line = ""

                                for j in remaining:
                                        line += self.data[i][j]

                                new_data.append(line)

                        k = 0

                        # calculate horizontal pair costs
                        left = pos_cut[0]
                        right = pos_cut[len(pos_cut) - 1]

                        for i in range(0, n):
                                for j in range(left + 1, right + 1):
                                        k += (self.data[i][j] != self.data[i][j - 1])

                        # calculate vertical pair costs
                        for i in range(1, n):
                                for j in pos_cut:
                                        k += (self.data[i][j] != self.data[i - 1][j])

                        cost = 1 + (k / len(pos_cut))
                        res.append(
                            Node(
                                new_data,
                                self.g + cost,
                                heuristic=hfunc,
                                via=via_columns(pos_cut)
                            )
                        )

                # cut rows
                for pos_cut in possible_cuts(n):
                        remaining = remaining_after_cut(pos_cut, n)

                        new_data = []

                        for i in remaining:
                                new_data.append(copy.deepcopy(self.data[i]))

                        res.append(
                            Node(
                                new_data,
                                self.g + (m / len(pos_cut)),
                                heuristic=hfunc,
                                via=via_rows(pos_cut)
                            )
                        )

                return res

def check_early(initial_state):
        # check if destination node is reachable

        n1, m1 = mat_size(initial_state)
        n2, m2 = mat_size(dest_data)

        return n1 >= n2 and m1 >= m2

def heuristic_trivial(state):
        if state == dest_data:
                return 0
        return sys.float_info.epsilon

def heuristic_a1(state):
        n1, m1 = mat_size(state)
        n2, m2 = mat_size(dest_data)

        if n2 > n1 or m2 > m1:
                return float('inf')

        if n1 == n2 and m1 == m2 and state == dest_data:
                return 0

        total_cost = 0

        row_surplus = n1 - n2
        if row_surplus > 0:
                total_cost += m2 / row_surplus

        col_surplus = m1 - m2
        if col_surplus > 0:
                total_cost += 1

        return total_cost

def heuristic_a2(state):
        n1, m1 = mat_size(state)
        n2, m2 = mat_size(dest_data)

        if n1 == n2 and m1 == m2 and state == dest_data:
                return 0

        if n2 > n1 or m2 > m1:
                return float('inf')

        cost = 0
        if n1 != n2:
                cost += sys.float_info.epsilon
        if m1 != m2:
                cost += 1

        return cost

def non_admissible_heuristic(state):
        n1, m1 = mat_size(state)
        n2, m2 = mat_size(dest_data)

        if n2 > n1 or m2 > m1:
                return float('inf')

        if state == dest_data:
                return 0

        return max(sys.float_info.epsilon, n1 - n2 + m1 - m2)

@stopit.threading_timeoutable(default="1")
def bfs():
        global sols_found
        global max_nodes_in_mem

        src = Node(src_data, 0)
        dest = Node(dest_data, -1)

        q = queue.Queue()
        q.put([src])
        while not q.empty():
                max_nodes_in_mem = max(max_nodes_in_mem, q.qsize())

                path_u = q.get()
                u = path_u[len(path_u) - 1]

                if u == dest:
                        print_path(path_u, "[ PATH ]")

                        sols_found += 1
                        if sols_found == max_sols:
                                break

                        continue

                for v in u.neighbours():
                        if v in path_u:
                                continue

                        new_path = copy.deepcopy(path_u)
                        new_path.append(v)
                        q.put(new_path)

        return "0"

@stopit.threading_timeoutable(default="1")
def dfs():
        src = Node(src_data, 0)
        dest = Node(dest_data, -1)

        dfs_impl([src], dest)
        return "0"

def dfs_impl(path_so_far, dest):
        global sols_found
        global max_nodes_in_mem

        max_nodes_in_mem = max(max_nodes_in_mem, len(path_so_far))

        if sols_found == max_sols:
                return

        u = path_so_far[len(path_so_far) - 1]

        if u == dest:
                print_path(path_so_far, "[ PATH ]")
                sols_found += 1
                return

        for v in u.neighbours():
                if v in path_so_far:
                        continue

                path_so_far.append(v)
                dfs_impl(path_so_far, dest)
                path_so_far.pop()

@stopit.threading_timeoutable(default="1")
def dfs_iterative():
        global sols_found
        global max_nodes_in_mem

        src = Node(src_data, 0)
        dest = Node(dest_data, -1)

        stack = [[src]]
        while len(stack) > 0:
                max_nodes_in_mem = max(max_nodes_in_mem, len(stack))

                path_u = stack.pop()
                u = path_u[len(path_u) - 1]

                if u == dest:
                        print_path(path_u, "[ PATH ]")

                        sols_found += 1
                        if sols_found == max_sols:
                                break

                        continue

                if not check_early(u.data):
                        continue

                for v in u.neighbours():
                        if v in path_u:
                                continue

                        new_path = copy.deepcopy(path_u)
                        new_path.append(v)
                        stack.append(new_path)

        return "0"

@stopit.threading_timeoutable(default="1")
def ida_star(hfunc):
        global max_sols
        global sols_found

        src = Node(src_data, 0, hfunc)
        dest = Node(dest_data, -1)

        bound = src.h
        while True:
                res = ida_star_impl([src], dest, bound, hfunc)

                if sols_found == max_sols:
                        break

                if res == float('inf'):
                        break

                bound = res

        return "0"

def ida_star_impl(path_so_far, dest, bound, hfunc):
        global sols_found
        global max_nodes_in_mem

        max_nodes_in_mem = max(max_nodes_in_mem, len(path_so_far))

        if sols_found == max_sols:
                return 0

        u = path_so_far[len(path_so_far) - 1]

        if u.f > bound:
                return u.f

        if u == dest and u.f == bound:
                print_path(path_so_far, "[ PATH ]")
                sols_found += 1

                if sols_found == max_sols:
                        return 0

        neighbours = u.neighbours(hfunc)
        neighbours = sorted(neighbours, key=lambda node: node.f)
        min_b = float('inf')
        for v in neighbours:
                if v in path_so_far:
                        continue

                path_so_far.append(v)
                res = ida_star_impl(path_so_far, dest, bound, hfunc)

                if sols_found == max_sols:
                        return 0

                if res < min_b:
                        min_b = res

                path_so_far.pop()

        return min_b

@stopit.threading_timeoutable(default="1")
def a_star(hfunc):
        global sols_found
        global max_nodes_in_mem

        src = Node(src_data, 0, hfunc)
        dest = Node(dest_data, -1)

        q = []
        heapq.heappush(q, (get_f([src]), [src]))
        while len(q) > 0:
                max_nodes_in_mem = max(max_nodes_in_mem, len(q))

                _, path_u = heapq.heappop(q)
                u = path_u[len(path_u) - 1]

                if u == dest:
                        print_path(path_u, "[ PATH ]")

                        sols_found += 1
                        if sols_found == max_sols:
                                break

                        continue

                for v in u.neighbours(hfunc):
                        if v in path_u:
                                continue

                        new_path = copy.deepcopy(path_u)
                        new_path.append(v)
                        heapq.heappush(q, (get_f(new_path), new_path))

        return "0"

def main(argv):
        global src_data
        global dest_data
        global max_sols
        global output_file

        argc = len(argv)

        if argc < 2:
                printerr("Error: not enough cli arguments.")
                printerr(usage)
                exit(1)

        output_dir  = "."
        filename    = ""
        timeout_sec = 60
        try:
                for i in range(1, argc):
                        if argv[i] == "--timeout" or argv[i] == "-t":
                                timeout_sec = float(argv[i + 1])
                                i += 1

                        if argv[i] == "--file" or argv[i] == "-f":
                                filename = argv[i + 1]
                                i += 1

                        if argv[i] == "--stop-after" or argv[i] == "-s":
                                max_sols = int(argv[i + 1])
                                i += 1

                        if argv[i] == "--output-dir":
                                output_dir = argv[i + 1]
                                i += 1

                if filename == "":
                        raise Exception('')

        except:
                printerr("Erorr in cli args.")
                printerr(usage)
                exit(1)

        # read file into string
        lines = lines_from_file(filename)

        # get source and destination from input
        i = 0
        for _ in range(0, len(lines)):
                if lines[i] == "":
                        i += 1
                        break

                src_data.append(lines[i])
                i += 1

        for j in range(i, len(lines)):
                if lines[j] == "":
                        continue

                dest_data.append(lines[j])

        # check input validity
        if not (check_full_rows(src_data) and check_full_rows(dest_data)):
                printerr("Invalid input.")
                exit(1)

        # check if solutions are possible
        if not check_early(src_data):
                mprint("No solutions possible for any search algorithm.")
                return

        # tables for algorithms and heuristics
        methods_normal = [
            ("bfs",           bfs),
            ("dfs",           dfs),
            ("dfs_iterative", dfs_iterative)
        ]

        methods_informed = [
            ("ida_star", ida_star),
            ("a_star",   a_star)
        ]

        heuristics = [
            ("trivial",        heuristic_trivial),
            ("admissible_1",   heuristic_a1),
            ("admissible_2",   heuristic_a2),
            ("non_admissible", non_admissible_heuristic)
        ]

        # search with all methods
        for mname, mfunc in methods_normal:
                output_filename = "{}/{}.out".format(output_dir, mname)
                output_file     = open(output_filename, "w")

                mprint("Searching with algorithm: {}\n".format(mname))

                reset_global_state()

                # apply search algorithm
                res = mfunc(timeout=timeout_sec)
                print_alg_info(res)

                output_file.close()

        for (mname, mfunc), (hname, hfunc) in itertools.product(methods_informed, heuristics):
                output_filename = "{}/{}-{}.out".format(output_dir, mname, hname)
                output_file     = open(output_filename, "w")

                mprint("Searching with algorithm: {}".format(mname))
                mprint("Using heuristic: {}\n".format(hname))

                reset_global_state()

                # apply search algorithm
                res = mfunc(hfunc, timeout=timeout_sec)
                print_alg_info(res)

                output_file.close()


if __name__ == "__main__":
        main(sys.argv)
