import pygame
from typing import Union


class Board(pygame.Surface):
    def __init__(self, block_size: int = 10, blocks_x: int = 10, blocks_y: int = 10, *args, **kwargs):
        self.size = (block_size * blocks_x, block_size * blocks_y)
        super().__init__(self.size, *args, **kwargs)
        self.block_size = block_size
        self.blocks_x = blocks_x
        self.blocks_y = blocks_y
        self.tiles = []
        self.clear()

    @property
    def width(self):
        return self.block_size * self.blocks_x

    @property
    def height(self):
        return self.block_size * self.blocks_y

    def init_tiles(self):
        for _ in range(self.blocks_y):
            temp = []
            for _ in range(self.blocks_x):
                temp.append((0, 0, 0))
            self.tiles.append(temp)

    def clear(self):
        self.tiles = []
        self.init_tiles()

    def tile(self, x: int = 0, y: int = 0, value: tuple = None) -> Union[None, tuple]:
        if value is not None:
            self.tiles[x][y] = value
        else:
            try:
                return self.tiles[x][y]
            except IndexError:
                return 255, 255, 255

    def update(self):
        self.fill((0, 0, 0))
        for x, x_tiles in enumerate(self.tiles):
            for y, y_tile in enumerate(x_tiles):
                start_x = x * self.block_size
                start_y = y * self.block_size
                end_x = (x + 1) * self.block_size
                end_y = (y + 1) * self.block_size
                self.fill(y_tile, (start_x, start_y, end_x, end_y))
