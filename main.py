from typing import Tuple

import pygame
import math
from queue import PriorityQueue
from colors import *
from node import Node

# basic windows variables
size = 800
win = pygame.display.set_mode((size, size))
pygame.display.set_caption("A* pathfinding algorithm")


# for manhattan distance (that is vertical plus horizontal)
def heuristic(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        if not current.is_start() and not current.is_end():
            current.make_path()
        draw()


# A* algorithm function
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = heuristic(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid


def draw_grid(window, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(window, grey, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(window, grey, (j * gap, 0), (j * gap, width))


def draw(window, grid, rows, width):
    window.fill(white)

    for row in grid:
        for node in row:
            if node.row == 0 or node.row == node.total_rows - 1 or node.col == 0 or node.col == node.total_rows - 1:
                node.make_barrier()
            node.draw(window)

    draw_grid(window, rows, width)
    pygame.display.update()


def get_mouse_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def main(window, width):
    rows = 50
    grid = make_grid(rows, width)

    start_node: Node = None
    end_node: Node = None

    run = True
    started = False

    while run:
        draw(window, grid, rows, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:  # left mb
                pos = pygame.mouse.get_pos()
                row, col = get_mouse_pos(pos, rows, width)
                node: Node = grid[row][col]
                if not start_node and node != end_node:
                    start_node = node
                    start_node.make_start()

                elif not end_node and node != start_node:
                    end_node = node
                    end_node.make_end()

                elif node != start_node and node != end_node:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # right mb
                pos = pygame.mouse.get_pos()
                row, col = get_mouse_pos(pos, rows, width)
                node: Node = grid[row][col]
                node.reset()

                if node == start_node:
                    start_node = None
                elif node == end_node:
                    end_node = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started and start_node and end_node:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    algorithm(lambda: draw(window, grid, rows, width), grid, start_node, end_node)  # anonymous function

                if event.key == pygame.K_c:
                    start_node = None
                    end_node = None
                    grid = make_grid(rows, width)

    pygame.quit()


if __name__ == "__main__":
    main(win, size)
