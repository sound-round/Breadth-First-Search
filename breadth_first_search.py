from collections import deque
from tkinter import *
import random
import time
import pandas as pd
import numpy as np
import logging


CELL_SIZE = 30
WIDTH = 30
HEIGHT = 20
ROBOT_COLOR = "#FF0000"
PATH_COLOR = "#00FF00"
TARGET_COLOR = "#0000FF"
ORDER_START_COLOR = "#00ddFF"
ORDER_END_COLOR = "#ffdd00"
ORDER_LINE_COLOR = "#000000"
BARRIER_COLOR = "#505050"
START = (10, 7)
TARGET = (20, 7)


def configure_logging():
    logging.basicConfig(
        filename='log.log',
        filemode='w',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
    )


configure_logging()


class Order(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end


class Robot:
    def __init__(self, loc):
        self.loc = loc
        self.goods = False
        self.order = None
        self.path = None
        self.target = None
        self.route = None

    def find_path(self, orders):

        start_time = time.time() * 1000.0

        if not self.goods:
            orders_starts = [order.start for order in orders]
            search_result = breath_first_search(grid, self.loc, orders_starts)
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
        self.route = iter(self.path[1:])
        try:
            # stringCommand = "DDDDDDDD"
            # for char in stringCommand:
                # if char == "U":
                #     self.loc = self.loc + Point.UP
                # if char == "D":
                #     self.loc = self.loc + Point.DOWN
                # if char == "R":
                #     self.loc = self.loc + Point.RIGHT
            self.loc = self.route.__next__()
            self.path.pop(0)
            # TODO calc path once
            # search_result = breath_first_search(grid, self.loc, [self.target])
            # self.path = get_path(search_result[0], self.loc, self.target)
        except StopIteration:
            print('StopIteration')
            if self.target == self.order.end:
                orders.pop(orders.index(self.order))
            self.goods = not self.goods
            self.route = None
            if orders:
                robot.find_path(orders)
        end_time = time.time() * 1000.0
        logging.info('robot walk time: %d', end_time - start_time)


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.barriers = []

    def in_bounds(self, point):
        (x, y) = point
        return 0 <= x < self.width / CELL_SIZE and 0 <= y < self.height / CELL_SIZE

    def is_not_barrier(self, point):
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


barriers = pd.DataFrame(
    np.zeros([HEIGHT, WIDTH]) * np.nan,
).replace({np.nan: None})
print(barriers)


grid = Grid(WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE)
grid.barriers = barriers

window = Tk()
window.title('breath_first_search')
canvas = Canvas(
    window,
    background='light grey',
    width=WIDTH * CELL_SIZE,
    height=HEIGHT * CELL_SIZE,
)


orders = []
for x in range(1, 40):
    # TODO delete from barriers
    orders.append(Order(
        (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)),
        (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
    ))


robot = Robot(START)
robot.find_path(orders)

# input example
# program:
# UUUUURRRRRRTUUUUUUPRRRRRRRRDDDDDDTLLLLLLLP
# server: 10
# 100 100 300 300
# 22 10 30 30

def on_click(event):
    #TODO do not place barrier at order
    global barriers

    x = int(event.x / CELL_SIZE)
    y = int(event.y / CELL_SIZE)
    if barriers[x][y]:
        barriers[x][y] = None
    else:
        barriers[x][y] = True

    startMs = time.time() * 1000.0
    possible_paths = breath_first_search(grid, robot.loc)
    robot.path = get_path(possible_paths[0], robot.loc, robot.target)
    robot.walk()
    endMs = time.time() * 1000.0
    print('shortest_path: ', robot.path, endMs - startMs )

    print("mouse click " + str(x) + " " + str(y) + " barriers size=" + str(len(barriers)))


canvas.bind("<Button-1>", on_click)


def draw_grid():
    for line in range(0, WIDTH * CELL_SIZE, CELL_SIZE):
        canvas.create_line([(line, 0), (line, HEIGHT * CELL_SIZE)], fill='grey', tags='grid_line_w')
    for line in range(0, HEIGHT * CELL_SIZE, CELL_SIZE):
        canvas.create_line([(0, line), (WIDTH * CELL_SIZE, line)], fill='grey', tags='grid_line_h')
    canvas.grid(row=0, column=0)


def draw_rect_at(x, y, color):
    x *= CELL_SIZE
    y *= CELL_SIZE
    canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=color)


def draw_line_at(start, end, color):
    canvas.create_line(
        start[0] * CELL_SIZE + CELL_SIZE / 2,
        start[1] * CELL_SIZE + CELL_SIZE / 2,
        end[0] * CELL_SIZE + CELL_SIZE / 2,
        end[1] * CELL_SIZE + CELL_SIZE / 2,
        fill=color
    )


def draw_orders():
    for order in orders:

        draw_rect_at(order.start[0], order.start[1], ORDER_START_COLOR)
        draw_rect_at(order.end[0], order.end[1], ORDER_END_COLOR)
        draw_line_at(order.start, order.end, ORDER_LINE_COLOR)

lastFrameStartMs = time.time() * 1000

def draw():
    global lastFrameStartMs
    currentMs = time.time() * 1000
    logging.info('time since last frame: %d', currentMs - lastFrameStartMs)
    lastFrameStartMs = currentMs
    canvas.delete("all")

    canvas.create_rectangle(0, 0, 1024, 1024, fill="#FFFFFF")
    draw_grid()
    draw_orders()
    robot_x, robot_y = robot.loc
    target_x, target_y = robot.target
    draw_rect_at(robot_x, robot_y, ROBOT_COLOR)
    draw_rect_at(target_x, target_y, TARGET_COLOR)
    for point in robot.path[1:-1]:
        x, y = point
        draw_rect_at(x, y, PATH_COLOR)

    for x in barriers.columns:
        for y in barriers.index:
            if barriers[x][y]:
                draw_rect_at(x, y, BARRIER_COLOR)


def do_loop():
    if orders:
        robot.walk()
    else:
        print('finish!')
        exit(0)
    draw()
    window.after(int(1000 / 15), do_loop)

do_loop()

window.mainloop()
