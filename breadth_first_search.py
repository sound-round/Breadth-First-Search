from collections import deque
from tkinter import *
import random
import time
import pandas as pd
import numpy as np


CELL_SIZE = 20
WIDTH = 30
HEIGHT = 20
START_COLOR = "#FF0000"
PATH_COLOR = "#00FF00"
FINISH_COLOR = "#0000FF"
ORDER_START_COLOR = "#00ddFF"
ORDER_END_COLOR = "#ffdd00"
ORDER_LINE_COLOR = "#000000"
BARRIER_COLOR = "#505050"
START = (10, 7)
FINISH = (20, 7)


ORDERS = []


barriers = pd.DataFrame(
    np.zeros([HEIGHT, WIDTH]) * np.nan,
).replace({np.nan: None})
print(barriers)


class Order(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end


for x in range(1, 10):
    # TODO delete from barriers
    ORDERS.append(Order(
        (random.randint(0, WIDTH), random.randint(0, HEIGHT)),
        (random.randint(0, WIDTH), random.randint(0, HEIGHT))
    ))


# PROFIT = MAX_TIPS - ORDER.CREATED - DELIVERY_TIME

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
        (x, y) = point
        # East, West, North, South
        neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]
        # South, North, West, East
        if (x + y) % 2 == 0:
            neighbors.reverse()
        results = filter(self.in_bounds, neighbors)
        results = filter(self.is_not_barrier, results)
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


def breath_first_search(graph, start_point):
    frontier = Queue()
    frontier.put(start_point)
    came_from = dict()
    came_from[start_point] = None

    while not frontier.is_empty():
        current_point = frontier.get_next_point()

        for next_point in graph.get_neighbors(current_point):
            if next_point not in came_from:
                frontier.put(next_point)
                came_from[next_point] = current_point

    return came_from


# start must be the same that was in breath_first_search
def get_path(came_from, start_point, finish_point):
    current_point = finish_point
    path = []

    while current_point != start_point:
        path.append(current_point)
        current_point = came_from[current_point]
    path.append(start_point)
    path.reverse()
    return path


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
    pass


def draw_orders():
    for order in ORDERS:

        draw_rect_at(order.start[0], order.start[1], ORDER_START_COLOR)
        draw_rect_at(order.end[0], order.end[1], ORDER_END_COLOR)
        draw_line_at(order.start, order.end, ORDER_LINE_COLOR)


possible_paths = breath_first_search(grid, START)
shortest_path = get_path(possible_paths, START, FINISH)


def on_click(event):
    global barriers
    global shortest_path

    x = int(event.x / CELL_SIZE)
    y = int(event.y / CELL_SIZE)
    if barriers[x][y]:
        # print(barriers.index((x, y)))
        barriers[x][y] = None
    else:
        barriers[x][y] = True

    startMs = time.time() * 1000.0
    possible_paths = breath_first_search(grid, START)
    shortest_path = get_path(possible_paths, START, FINISH)
    endMs = time.time() * 1000.0
    print('shortest_path: ', shortest_path, endMs - startMs )

    print("mouse click " + str(x) + " " + str(y) + " barriers size=" + str(len(barriers)))


canvas.bind("<Button-1>", on_click)


def draw():
    canvas.create_rectangle(0, 0, 1024, 1024, fill="#FFFFFF")
    draw_grid()
    # for x in range(0, WIDTH):
    #     for y in range(0, HEIGHT):
    #         draw_rect_at(x, y, START_COLOR)
    start_x, start_y = START
    finish_x, finish_y = FINISH
    draw_rect_at(start_x, start_y, START_COLOR)
    draw_rect_at(finish_x, finish_y, FINISH_COLOR)
    for point in shortest_path[1:-1]:
        x, y = point
        draw_rect_at(x, y, PATH_COLOR)

    for x in barriers.columns:
        for y in barriers.index:
            if barriers[x][y]:
                draw_rect_at(x, y, BARRIER_COLOR)

    # for point in barriers:
    #     x, y = point
    #     draw_rect_at(x, y, BARRIER_COLOR)

    draw_orders()


def do_loop():
    draw()
    window.after(int(1000 / 15), do_loop)


do_loop()
window.mainloop()
