from collections import deque
from tkinter import *

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


grid = Grid(30, 20)
grid.barriers = [(15, 5), (15, 6), (15, 7), (15, 8), (15, 9)]
start = (10, 7)
finish = (20, 7)
possible_paths = breath_first_search(grid, start)
# print('came_from: ', came_from)

shortest_path = get_path(possible_paths, start, finish)
print('shortest_path: ', shortest_path)

# CELL_SIZE = 32
#
# WIDTH = 30
# HEIGHT = 20
#
# userX = 5
# userY = 1
#
# currentTick = 0
#
# window = Tk()
# window.wm_title("breath_first_search")
#
# canvas = Canvas(window, width=WIDTH * CELL_SIZE, height=HEIGHT * CELL_SIZE)
# canvas.pack()
#
# def draw():
#     def draw_rect_at(x, y, color, width=0):
#         x *= CELL_SIZE
#         y *= CELL_SIZE
#         canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=color)
#
#     for x in range(0, WIDTH):
#         for y in range(0, HEIGHT):
#             draw_rect_at(x, y)
#
#     draw_rect_at(userX, userY, PLAYER_COLOR, 1)
#
#
# def do_loop():
#
#     draw()
#     window.after(int(1000 / 15), do_loop)
#
#
# do_loop()
# window.mainloop()
