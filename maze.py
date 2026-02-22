import json
import math

class Maze:
    def __init__(self, level_path):
        with open(level_path, "r") as f:
            data = json.load(f)

        self.map = data["map"]
        self.height = len(self.map)
        self.width = len(self.map[0])

        self.player_start = None
        self.monster_start = None
        self.exit = None
        self.fake_exits = []
        self.compass_pos = None
        self.compass_taken = False

        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                pos = (x + 0.5, y + 0.5)
                if cell == "P":
                    self.player_start = pos
                elif cell == "M":
                    self.monster_start = pos
                elif cell == "E":
                    self.exit = (x, y)
                elif cell == "F":
                    self.fake_exits.append((x, y))
                elif cell == "C":
                    self.compass_pos = pos

    def is_wall(self, x, y):
        xi, yi = int(x), int(y)
        if xi < 0 or yi < 0 or xi >= self.width or yi >= self.height:
            return True
        return self.map[yi][xi] == "#"

    def reached_real_exit(self, x, y):
        return int(x) == self.exit[0] and int(y) == self.exit[1]

    def reached_fake_exit(self, x, y):
        return (int(x), int(y)) in self.fake_exits

    def check_compass_pickup(self, x, y):
        if self.compass_pos and not self.compass_taken:
            if math.hypot(x - self.compass_pos[0], y - self.compass_pos[1]) < 0.6:
                self.compass_taken = True

    def compass_angle(self, px, py):
        if not self.compass_taken:
            return None
        dx = self.exit[0] + 0.5 - px
        dy = self.exit[1] + 0.5 - py
        return math.atan2(dy, dx)