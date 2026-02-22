from settings import *

class Player:
    def __init__(self, start_pos):
        self.x, self.y = start_pos
        self.angle = 0
        self.stamina = STAMINA_MAX

    def move(self, dx, dy, maze):
        nx = self.x + dx
        ny = self.y + dy

        # Axis-separated collision (prevents wall clipping)
        if not maze.is_wall(nx, self.y):
            self.x = nx
        if not maze.is_wall(self.x, ny):
            self.y = ny