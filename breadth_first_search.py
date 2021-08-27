from collections import deque
from tkinter import *


CELL_SIZE = 20
WIDTH = 30
HEIGHT = 20
START_COLOR = "#FF0000"
PATH_COLOR = "#00FF00"
FINISH_COLOR = "#0000FF"
BARRIER_COLOR = "#000000"
START = (10, 7)
FINISH = (20, 7)
BARRIERS = [(15, 5), (15, 6), (15, 7), (15, 8), (15, 9)]



class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.barriers = []

    def in_bounds(self, point):
        (x, y) = point
        return 0 <= x < self.width and 0 <= y < self.height

    def is_not_barrier(self, point):
        return point not in self.barriers

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
grid.barriers = BARRIERS
possible_paths = breath_first_search(grid, START)
shortest_path = get_path(possible_paths, START, FINISH)
print('shortest_path: ', shortest_path)


window = Tk()
window.title('breath_first_search')
canvas = Canvas(
    window,
    background='light grey',
    width=WIDTH * CELL_SIZE,
    height=HEIGHT * CELL_SIZE,
)
for line in range(0, WIDTH * CELL_SIZE, CELL_SIZE):  # range(start, stop, step)
    canvas.create_line([(line, 0), (line, HEIGHT * CELL_SIZE)], fill='white', tags='grid_line_w')

for line in range(0, HEIGHT * CELL_SIZE, CELL_SIZE):
    canvas.create_line([(0, line), (WIDTH * CELL_SIZE, line)], fill='white', tags='grid_line_h')
canvas.grid(row=0, column=0)


def draw():
    def draw_rect_at(x, y, color):
        x *= CELL_SIZE
        y *= CELL_SIZE
        canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=color)

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

    for point in BARRIERS:
        x, y = point
        draw_rect_at(x, y, BARRIER_COLOR)


def do_loop():
    draw()
    window.after(int(1000 / 15), do_loop)


do_loop()
window.mainloop()

