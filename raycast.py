import pygame
import math
from settings import *

def render(screen, player, maze, monsters):
    width = screen.get_width()
    height = screen.get_height()
    ray_angle = player.angle - FOV / 2
    ray_width = width // NUM_RAYS

    depth_buffer = []

    # ---------- WALLS ----------
    for ray in range(NUM_RAYS):
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        for depth in range(1, int(MAX_DEPTH * 100)):
            d = depth * 0.01
            x = player.x + cos_a * d
            y = player.y + sin_a * d

            if maze.is_wall(x, y):
                d *= math.cos(player.angle - ray_angle)
                depth_buffer.append(d)

                h = min(height, int(height / (d + 0.0001)))
                shade = max(20, 200 - int(d * 30))

                pygame.draw.rect(
                    screen,
                    (shade, shade, shade),
                    (ray * ray_width,
                     height // 2 - h // 2,
                     ray_width, h)
                )
                break

        ray_angle += FOV / NUM_RAYS

    # ---------- SPRITE HELPER ----------
    def draw_sprite(x, y, color):
        dx = x - player.x
        dy = y - player.y
        dist = math.hypot(dx, dy)
        if dist < 0.3:
            return

        angle = math.atan2(dy, dx)
        diff = angle - player.angle
        diff = (diff + math.pi) % (math.tau) - math.pi

        if abs(diff) > FOV / 2:
            return

        screen_x = int((diff + FOV / 2) / FOV * width)
        size = int(height / (dist + 0.0001))
        y_pos = height // 2 - size // 2

        ray_index = int(screen_x / ray_width)
        if 0 <= ray_index < len(depth_buffer):
            if dist < depth_buffer[ray_index]:
                pygame.draw.rect(
                    screen,
                    color,
                    (screen_x - size // 2, y_pos, size, size)
                )

    # ---------- EXIT ----------
    if maze.exit:
        ex, ey = maze.exit
        draw_sprite(ex + 0.5, ey + 0.5, (0, 0, 0))

    # ---------- FAKE EXITS ----------
    for fx, fy in maze.fake_exits:
        draw_sprite(fx + 0.5, fy + 0.5, (40, 40, 40))

    # ---------- COMPASS (WORLD) ----------
    if maze.compass_pos and not maze.compass_taken:
        cx, cy = maze.compass_pos
        draw_sprite(cx, cy, (70, 70, 70))  # dark gray

    # ---------- MONSTERS ----------
    for monster in monsters:
        draw_sprite(
            monster.x,
            monster.y,
            {
                "red": (255, 0, 0),
                "blue": (0, 0, 255),
                "green": (0, 255, 0)
            }[monster.color]
        )