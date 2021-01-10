import neat
import numpy as np
import math
import random
import tilemap
from math import sqrt
from collections import namedtuple


def distance(x1: int, y1: int, x2: int, y2: int):
    return sqrt((x2-x1)**2 + (y2-y1)**2)


class Snake:
    def __init__(self, matrix: tilemap.Board, spawn_x: int = 0, spawn_y: int = 0, block_size: int = 0):
        self.x = spawn_x
        self.y = spawn_y
        self.block_size = block_size
        self.direction = 0  # Goes clockwise, starting at up
        self.matrix = matrix
        self.tiles = []
        self.init()
        self.alive = True
        self.ate_food = False

    def init(self):
        for y_offset in range(3):
            self.tiles.append((self.x, self.y + y_offset))

    def up(self):
        self.y -= 1
        self.update_tiles()

    def down(self):
        self.y += 1
        self.update_tiles()

    def left(self):
        self.x -= 1
        self.update_tiles()

    def right(self):
        self.x += 1
        self.update_tiles()

    def update_tiles(self):
        self.tiles.insert(0, (self.x, self.y))
        if self.ate_food:
            self.tiles.pop()
            self.ate_food = False

    def update(self):
        if not self.alive:
            self.tiles = []
            return
        for index, tile in enumerate(self.tiles):
            if index == 0 and self.matrix.tile(tile[0], tile[1]) == (255, 255, 255):
                self.alive = False
            if index == 0 and self.matrix.tile(tile[0], tile[1]) == (255, 0, 0):
                self.ate_food = True
            if self.alive:
                self.matrix.tile(tile[0], tile[1], (255, 255, 255))

    @property
    def length(self):
        return len(self.tiles)

    @property
    def head(self):
        Point = namedtuple("Point", ["x", "y"])
        return Point(self.tiles[0][0], self.tiles[0][1])

    def reward(self):
        r = 0
        if self.alive:
            r += self.length  # length of snake
        else:
            r = -1000000000000000
        return r

    def get_wall(self, x_change: int = 0, y_change: int = 0) -> namedtuple:
        changed = {"x": 0, "y": 0}
        while True:
            changed["x"] += x_change
            changed["y"] += y_change
            if self.matrix.tile(changed["x"], changed["y"]) == (255, 255, 255):
                break
        return changed["x"] + changed["y"]

    def find_food(self) -> namedtuple:
        Point = namedtuple("Point", ["x", "y"])
        for y in range(self.matrix.height):
            for x in range(self.matrix.width):
                if self.matrix.tile(x, y) == (255, 0, 0):
                    return Point(x, y)
        return Point(-1, -1)

    @property
    def direction_of_food(self) -> int:
        if self.find_food().y < self.head.y:
            return 0
        if self.find_food().x > self.head.x:
            return 1
        if self.find_food().y > self.head.y:
            return 2
        if self.find_food().x < self.head.x:
            return 3

    def get_data(self):
        radars = [-1, -1, -1, -1, -1, -1, -1]
        if not self.alive:
            return radars
        # Distance from food
        radars[5] = round(distance(self.head.x, self.find_food().x, self.head.y, self.find_food().y) * 100)
        # Direction of food
        radars[6] = self.direction_of_food
        if self.direction == 0:
            radars[0] = self.get_wall(x_change=-1)                  # Left
            radars[1] = self.get_wall(x_change=-1, y_change=-1)     # Up left
            radars[2] = self.get_wall(y_change=-1)                  # Up
            radars[3] = self.get_wall(x_change=1, y_change=-1)      # Up right
            radars[4] = self.get_wall(x_change=1)                   # Right
        elif self.direction == 1:
            radars[0] = self.get_wall(y_change=-1)                  # Top
            radars[1] = self.get_wall(x_change=1, y_change=-1)      # Up right
            radars[2] = self.get_wall(x_change=1)                   # Right
            radars[3] = self.get_wall(x_change=1, y_change=1)       # Down right
            radars[4] = self.get_wall(y_change=1)                   # Bottom
        elif self.direction == 2:
            radars[0] = self.get_wall(x_change=1)                   # Right
            radars[1] = self.get_wall(x_change=1, y_change=1)       # Down right
            radars[2] = self.get_wall(y_change=1)                   # Down
            radars[3] = self.get_wall(x_change=-1, y_change=1)      # Down left
            radars[4] = self.get_wall(x_change=-1)                  # Left
        elif self.direction == 3:
            radars[0] = self.get_wall(y_change=1)                   # Bottom
            radars[1] = self.get_wall(x_change=-1, y_change=1)      # Bottom left
            radars[2] = self.get_wall(x_change=-1)                  # Left
            radars[3] = self.get_wall(x_change=-1, y_change=-1)     # Top left
            radars[4] = self.get_wall(y_change=-1)                  # Top
        return radars
