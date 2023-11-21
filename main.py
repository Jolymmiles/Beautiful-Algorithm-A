import tkinter as tk
import heapq
import random
import sys
import colorsys

sys.setrecursionlimit(10000)


class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f


start = None
end = None
path_shown = None
maze = None
canvas = None

def generate_rainbow_color(start_color, end_color, progress):
    start_hsv = colorsys.rgb_to_hsv(*start_color)
    end_hsv = colorsys.rgb_to_hsv(*end_color)
    current_hue = start_hsv[0] + (end_hsv[0] - start_hsv[0]) * progress
    current_color = colorsys.hsv_to_rgb(current_hue, 1, 1)
    return tuple(int(x * 255) for x in current_color)

def a_star(maze, start, end):
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    open_list = []
    closed_list = []

    heapq.heappush(open_list, (start_node.f, start_node))

    while len(open_list) > 0:
        # Получаем текущий узел
        current_node = heapq.heappop(open_list)[1]
        closed_list.append(current_node)

        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (
                    len(maze[len(maze) - 1]) - 1) or node_position[1] < 0:
                continue

            if maze[node_position[0]][node_position[1]] != 0:
                continue

            new_node = Node(current_node, node_position)

            children.append(new_node)

        for child in children:
            if child in closed_list:
                continue

            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + (
                    (child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            if len([open_node for open_node in open_list if child == open_node[1] and child.g > open_node[1].g]) > 0:
                continue

            heapq.heappush(open_list, (child.f, child))

def animate_path(path, delay_ms, step_duration_ms):
    if not path:
        return

    def draw_next_step():
        nonlocal path_index
        if path_index < len(path):
            step = path[path_index]
            progress = path_index / len(path)  # Calculate progress from 0 to 1
            rainbow_color = generate_rainbow_color((0, 0, 255), (255, 0, 0), progress)  # Blue to Red gradient
            canvas.create_rectangle(step[1] * cell_size, step[0] * cell_size, step[1] * cell_size + cell_size,
                                    step[0] * cell_size + cell_size, fill="#%02x%02x%02x" % rainbow_color)
            path_index += 1
            root.after(step_duration_ms, draw_next_step)

    path_index = 0
    draw_next_step()

def on_canvas_click(event):
    global start, end, path_shown, maze, canvas

    x, y = event.x // cell_size, event.y // cell_size

    # Проверяем, чтобы клик был в пределах лабиринта
    if x >= maze_width or y >= maze_height:
        return

    if not start:
        start = (y, x)
        canvas.create_rectangle(x * cell_size, y * cell_size, x * cell_size + cell_size, y * cell_size + cell_size,
                                fill="green")
    elif not end:
        end = (y, x)
        canvas.create_rectangle(x * cell_size, y * cell_size, x * cell_size + cell_size, y * cell_size + cell_size,
                                fill="red")
        path = a_star(maze, start, end)
        if path:
            animate_path(path, 10, 10)  # Adjust delay_ms and step_duration_ms as needed for animation speed


def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]

    def carve_passages_from(x, y, depth=0):
        directions = [(x - 2, y), (x + 2, y), (x, y - 2), (x, y + 2)]
        random.shuffle(directions)

        for (nx, ny) in directions:
            if 0 <= nx < width and 0 <= ny < height:
                if maze[ny][nx] == 1:
                    maze[y + (ny - y) // 2][x + (nx - x) // 2] = 0
                    maze[ny][nx] = 0
                    carve_passages_from(nx, ny, depth + 1)

    start_x, start_y = random.randint(0, width - 1), random.randint(0, height - 1)
    maze[start_y][start_x] = 0
    carve_passages_from(start_x, start_y)

    return maze

def close_window(event=None):
    root.destroy()

def generate_new_maze():
    global maze, canvas, start, end
    maze = generate_maze(maze_width, maze_height)
    start, end = None, None
    draw_maze()

def draw_maze():
    canvas.delete("all")  # Очистка холста
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            color = "black" if maze[y][x] == 1 else "white"
            canvas.create_rectangle(x * cell_size, y * cell_size, x * cell_size + cell_size,
                                    y * cell_size + cell_size, fill=color, outline="black")

def handle_key_press(event):
    if event.char == 'r' or event.char == 'к':
        generate_new_maze()

root = tk.Tk()
root.title("A* Pathfinding")
root.attributes('-fullscreen', True)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

cell_size = 20
maze_width = screen_width // cell_size
maze_height = screen_height // cell_size

maze = generate_maze(maze_width, maze_height)

canvas = tk.Canvas(root, width=maze_width * cell_size, height=maze_height * cell_size, borderwidth=0, highlightthickness=0)
canvas.grid()
canvas.bind("<Button-1>", on_canvas_click)
root.bind('<Escape>', close_window)
root.bind('<Key>', handle_key_press)

for y in range(len(maze)):
    for x in range(len(maze[y])):
        color = "black" if maze[y][x] == 1 else "white"
        canvas.create_rectangle(x * cell_size, y * cell_size, x * cell_size + cell_size,
                                y * cell_size + cell_size, fill=color, outline="black")

root.mainloop()
