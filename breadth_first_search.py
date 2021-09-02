import io
from collections import deque
import time
import pandas as pd
import numpy as np
import logging

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def currentMs():
    return time.time() * 1000

tick = 0
robot = None
orders = []
totalTimeTookMs = 0

CELL_SIZE = 5

stopCommand = ""
for i in range(60):
    stopCommand += "S"
stopCommand += "\n"

class Robot:
    def __init__(self, loc):
        self.loc = loc
        self.goods = False
        self.order = None
        self.path = None
        self.target = None
        self.route = None
        self.commandline = []
        self.addition = []

    def find_path(self, orders):

        start_time = time.time() * 1000.0

        if not self.goods:
            orders_starts = [order.start for order in orders]
            # print('orders_starts:', orders_starts)
            if not orders_starts:
                self.path = None
                return
            search_result = breath_first_search(grid, self.loc, orders_starts)
            # eprint(search_result)
            #if search_result:
            self.order = [order for order in orders if order.start == search_result[1]][0]
            self.target = self.order.start
            self.path = get_path(search_result[0], self.loc, self.target)
            return
        self.target = self.order.end
        search_result = breath_first_search(grid, self.loc, [self.target])
        self.path = get_path(search_result[0], self.loc, self.target)
        end_time = time.time() * 1000.0
        logging.info('robot find path time: %d', end_time - start_time)
        return

    def walk(self):
        start_time = time.time() * 1000.0
        global orders
        # print('im here')
        if not self.route:
            if self.addition:
                self.route = iter(self.addition)
                self.commandline.extend(self.addition)
                self.addition = []
            else:
                self.route = iter(self.commandline)

        try:
            char = next(self.route)
            if char == "U":
                self.loc = (self.loc[0] -1 , self.loc[1])
            elif char == "D":
                self.loc = (self.loc[0] + 1, self.loc[1])
            elif char == "R":
                self.loc = (self.loc[0], self.loc[1] + 1)
            elif char == "L":
                self.loc = (self.loc[0], self.loc[1] - 1)
            elif char == 'P' or char == 'T':
                pass
            elif char == 'S':
                pass
        except StopIteration:
            if self.target == self.order.end and orders:
                orders.pop(orders.index(self.order))
            self.goods = not self.goods
            self.path = None

            if orders:
                self.find_path(orders)
            # print('stop_iter path:', self.path)
            self.route = None
            self.addition = self.create_commandline()

        end_time = time.time() * 1000.0
        logging.info('robot walk time: %d', end_time - start_time)

    def create_commandline(self):
        commandline = []
        if not self.path:
        #     if len(self.commandline) < 60:
        #         commandline.extend(['S' for x in range(60-len(self.commandline))])
            return
        for i in range(len(self.path)):
            if self.path[i] == self.path[-1]:
                if self.goods:
                    commandline.append('P')
                else:
                    commandline.append('T')
                continue
            shift_x = self.path[i + 1][0] - self.path[i][0]
            shift_y = self.path[i + 1][1] - self.path[i][1]
            shift = (shift_x, shift_y)
            if shift == (0, 1):
                commandline.append('R')
            elif shift == (0, -1):
                commandline.append('L')
            elif shift == (1, 0):
                commandline.append('D')
            elif shift == (-1, 0):
                commandline.append('U')
        return commandline


class Order(object):
    def __init__(self, start, end, createdAt):
        self.start = start
        self.end = end
        self.createdAt = createdAt



class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.barriers = []

    def in_bounds(self, point):
        (x, y) = point
        return 0 < x <= self.width / CELL_SIZE and 0 < y <= self.height / CELL_SIZE

    def is_not_barrier(self, point):
        # TODO use plain arrays
        return not self.barriers[point[0]][point[1]]
        #  return point not in self.barriers  # TODO OPTIMIZE - SLOW PART

    def get_neighbors(self, point):
        start_time = time.time() * 1000.0
        (x, y) = point
        # East, West, North, South
        neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]
        # South, North, West, East
        if (x + y) % 2 == 0:
            neighbors.reverse()
        results = filter(self.in_bounds, neighbors)
        results = filter(self.is_not_barrier, results)
        end_time = time.time() * 1000.0
        # logging.info('get_neighbors time: %d', end_time - start_time)
        return results


class Queue:
    def __init__(self):
        self.queue = deque()

    def get_next_point(self):
        return self.queue.popleft()

    def put(self, point):
        self.queue.append(point)

    def is_empty(self):
        return not self.queue


def breath_first_search(graph, start_point, finish_points: list = []):
    start_time = time.time() * 1000.0
    frontier = Queue()
    frontier.put(start_point)
    came_from = dict()
    came_from[start_point] = None
    target_point = None

    while not frontier.is_empty():
        current_point = frontier.get_next_point()

        if current_point in finish_points:
            target_point = current_point
            break

        for next_point in graph.get_neighbors(current_point):
            if next_point not in came_from:
                frontier.put(next_point)
                came_from[next_point] = current_point
    end_time = time.time() * 1000.0
    logging.info('breath_first_search time: %d', end_time - start_time)
    return came_from, target_point


# start must be the same that was in breath_first_search
def get_path(came_from, start_point, finish_point):
    start_time = time.time() * 1000.0
    current_point = finish_point
    path = []

    while current_point != start_point:
        path.append(current_point)
        current_point = came_from[current_point]
    path.append(start_point)
    path.reverse()
    end_time = time.time() * 1000.0
    logging.info('get_path time: %d', end_time - start_time)
    return path


def main():
    global barriers, robot, grid, totalTimeTookMs
    # f = open('/var/tmp/01', 'r')
    f = io.open(sys.stdin.fileno())
    first_str = f.readline().split(' ')
    N = int(first_str[0])
    max_tips = int(first_str[1])
    cost = int(first_str[2])
    # print('N:', N, 'MAX_tips:', max_tips, 'cost:', cost)
    map_ = f.readlines(N * N)

    # print(formatted_map)
    barriers = pd.DataFrame(
        np.zeros([N, N]) * np.nan,
        index=[x for x in range(1, N + 1)],
        columns=[x for x in range(1, N + 1)]
    ).replace({np.nan: None})

    def add_barriers(map_):
        for y, line in enumerate(map_):
            for x, point in enumerate(line):
                if point == '#':
                    barriers[x + 1][y + 1] = True

    add_barriers(map_)
    # print(barriers)
    second_str = f.readline().split(' ')
    # f.flush()
    n_iters = int(second_str[0])
    n_orders = int(second_str[1])
    # print('n_iters:', n_iters, 'n_orders:', n_orders)
    # TODO output R(robots) and coordinates
    sys.stdout.write(str(1) + '\n')
    for x in range(N):
        for y in range(N):
            if barriers[x + 1][y + 1] is None and robot is None:
                robot = Robot((x + 1, y + 1))
                sys.stdout.write(f'{y + 1} {x + 1}\n')
                sys.stdout.flush()

    def get_orders(file):
        n_orders_str = file.readline()
        if (n_orders_str == ""):
            n_orders_str = file.readline()

        n_orders = int(n_orders_str)
        new_orders = []
        for i in range(n_orders):
            order = file.readline().split()
            new_orders.append(order)
        return new_orders

    def add_orders(new_orders):
        global orders
        for order in new_orders:
            orders.append(Order(
                (int(order[0]), int(order[1])),
                (int(order[2]), int(order[3])),
                tick
            ))

    # new_orders = get_orders(f)
    # print('orders:', new_orders)

    # add_orders(new_orders)
    # print('orders:', orders)
    grid = Grid(N * CELL_SIZE, N * CELL_SIZE)
    grid.barriers = barriers
    rest = []

    for i in range(n_iters):
        if totalTimeTookMs > 15000:
            sys.stdout.write(stopCommand)
            sys.stdout.flush()
            continue

        f.flush()
        new_orders = get_orders(f)
        f.flush()

        startMs = currentMs()

        # print('new_orders!!!', new_orders)
        if new_orders:
            add_orders(new_orders)
        if rest:
            robot.commandline = rest

        if not robot.path:
            robot.find_path(orders)
            robot.commandline = robot.create_commandline()
        k = 0
        # robot.find_path(orders)
        while k < 60 and robot.path:
            robot.walk()
            # print('robot_loc in cicle', robot.loc)
            k += 1
        # print('finish commandline from main:', robot.commandline)
        # print('len cl:', len(robot.commandline))
        if not robot.commandline:
            robot.commandline = ['S' for x in range(60)]
        if len(robot.commandline) > 60:
            rest = robot.commandline[60:]
            robot.commandline = robot.commandline[:60]
        if len(robot.commandline) < 60:
            robot.commandline.extend(['S' for x in range(60 - len(robot.commandline))])
        # print('finish commandline from main:', robot.commandline)
        # print('len cl:', len(robot.commandline))
        sys.stdout.write(''.join(robot.commandline) + '\n')
        sys.stdout.flush()
        robot.commandline = []

        endMs = currentMs()

        totalTimeTookMs = totalTimeTookMs + (endMs - startMs)

        # print('robot_loc:', robot.loc)

import traceback

try:
    main()
except BaseException:
    tb = traceback.format_exc()
    print(tb)

