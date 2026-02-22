import math
import random
from settings import *

class Monster:
    def __init__(self, color, start_pos):
        self.x, self.y = start_pos
        self.color = color
        self.target = None  # Random roam target
        self.reach_thresh = 0.3  # how close to reach target

    def can_see_player(self, player, maze):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 8:  # max vision range
            return False

        angle = math.atan2(dy, dx)
        step = 0.1
        for i in range(int(dist / step)):
            x = self.x + math.cos(angle) * step * i
            y = self.y + math.sin(angle) * step * i
            if maze.is_wall(x, y):
                return False
        return True

    def caught_player(self, player):
        return math.hypot(self.x - player.x, self.y - player.y) < 0.6

    def try_move(self, dx, dy, maze):
        nx = self.x + dx
        ny = self.y + dy
        if not maze.is_wall(nx, self.y):
            self.x = nx
        if not maze.is_wall(self.x, ny):
            self.y = ny

    def update(self, player, maze, looking):
        speed = MONSTER_SPEED / 60

        # Blue = stops if looking, Green = moves only when looked at
        if self.color == "blue" and looking:
            return
        if self.color == "green" and not looking:
            return

        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        dist_to_player = math.hypot(dx, dy)

        # ---------------- CHASE PLAYER ----------------
        if self.can_see_player(player, maze) and dist_to_player <= 3:
            self.angle = math.atan2(dy, dx)
        else:
            # ---------------- RANDOM ROAM ----------------
            if self.target is None or math.hypot(self.target[0]-self.x, self.target[1]-self.y) < self.reach_thresh:
                # Pick a new random free tile in the maze
                free_tiles = [(x+0.5, y+0.5)
                              for y in range(maze.height)
                              for x in range(maze.width)
                              if not maze.is_wall(x, y)]
                self.target = random.choice(free_tiles)
            dx_t = self.target[0] - self.x
            dy_t = self.target[1] - self.y
            self.angle = math.atan2(dy_t, dx_t)

        # Move forward
        dx_move = math.cos(self.angle) * speed
        dy_move = math.sin(self.angle) * speed
        self.try_move(dx_move, dy_move, maze)