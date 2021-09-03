import io
from collections import deque
import time
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

stop_сommand = ""
for i in range(60):
    stop_сommand += "S"
stop_сommand += "\n"


class Robot:
    def __init__(self, loc):
        self.loc = loc
        self.goods = False
        self.order = None
        self.path = None
        self.target = None
        self.cur_route = None
        self.full_route = []
        self.commandline = []
        self.addition = []

    def find_path(self, orders):

        # start_time = time.time() * 1000.0

        if not self.goods:
            orders_starts = [order.start for order in orders]
            #print('orders_starts:', orders_starts)
            if not orders_starts:
                self.path = None
                return
            search_result = breath_first_search(grid, self.loc, orders_starts)
            #print('search res', search_result)
            self.order = [order for order in orders if order.start == search_result[1]][0]
            print('self_ordrr', self.order.start)
            self.target = self.order.start
            self.path = get_path(search_result[0], self.loc, self.target)
            #print('selfpath', self.path)
            return
        self.target = self.order.end
        #print('orderEND', self.order.end)
        search_result = breath_first_search(grid, self.loc, [self.target])
        #print('search_result!!!', search_result)
        self.path = get_path(search_result[0], self.loc, self.target)
        #print('SELFPATH', self.path)
        return

    def walk(self):
        start_time = time.time() * 1000.0
        global orders
        if not self.cur_route:
            self.cur_route = iter(self.full_route)
            self.full_route = []
        try:
            char = next(self.cur_route)
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
            self.goods = not self.goods
            if self.target == self.order.end and orders:
                print('SELF ORDER:', self.order.start, self.order.end)
                for order in orders:
                    print('order in orders', order.start, order.end)
                print('del')
                orders.pop(orders.index(self.order))
            if orders:
                self.find_path(orders)

            #print('path in walk', self.path)
            addition = self.create_commandline()
            if addition:
                self.full_route.extend(addition)
                #print('self full route', self.full_route)
                self.commandline.extend(addition)
            self.cur_route = []

        end_time = time.time() * 1000.0
        logging.info('robot walk time: %d', end_time - start_time)

    def create_commandline(self):
        commandline = []
        if not self.path:
            return commandline
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
    def __init__(self, start, end, created_at):
        self.start = start
        self.end = end
        self.createdAt = created_at


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
        return not self.barriers[point[1] - 1][point[0] - 1]
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
        #print('came_from',came_from)
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
    barriers = [] # x y
   # barriers[y][x]
    def add_barriers(map_):
        for y, line in enumerate(map_):
            barriers.append([])
            for x, point in enumerate(line):
                barriers[y].append(point == '#')

    add_barriers(map_)
    # print(barriers)
    second_str = f.readline().split(' ')
    # f.flush()
    n_iters = int(second_str[0])
    n_orders = int(second_str[1])
    # print('n_iters:', n_iters, 'n_orders:', n_orders)

    sys.stdout.write(str(1) + '\n')
    for x in range(N):
        for y in range(N):
            if barriers[y][x] == False and robot is None:
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

    for i in range(n_iters):
        if totalTimeTookMs > 15000:
            sys.stdout.write(stop_сommand)
            sys.stdout.flush()
            continue
        f.flush()
        new_orders = get_orders(f)
        f.flush()
        startMs = currentMs()
        #print('new_orders', new_orders)
        if new_orders:
            add_orders(new_orders)
        if not robot.path and orders:
            robot.find_path(orders)
            #print('rob path:', robot.path)
            command_line = robot.create_commandline()
            #print('new_cl', command_line)
            robot.commandline.extend(command_line)
            robot.full_route.extend(command_line)
        k = 0
        #print('!!!ORDERS:' , orders)
        while k < 60 and robot.path:
            robot.walk()
            k += 1

        if not robot.commandline:
            robot.commandline = ['S' for x in range(60)]
        if len(robot.commandline) < 60:
            robot.commandline.extend(['S' for x in range(60 - len(robot.commandline))])

        cl_to_send = robot.commandline[:60]

        sys.stdout.write(''.join(cl_to_send) + '\n')
        sys.stdout.flush()
        del robot.commandline[:60]

        endMs = currentMs()

        tookMs = endMs - startMs
        totalTimeTookMs = totalTimeTookMs + (tookMs)


import traceback

try:
    main()
except BaseException:
    tb = traceback.format_exc()
    print(tb)
