import pygame
import math
import sys
import os
from PyQt5.QtWidgets import QApplication, QFileDialog

from settings import *
from maze import Maze
from player import Player
from monster import Monster
from raycast import render
from ui import overlay, game_over_screen, win_screen

pygame.init()
pygame.display.set_caption("Maze Game")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
fullscreen = False

# ---------------- FULLSCREEN ----------------
def toggle_fullscreen():
    global screen, fullscreen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

# ---------------- FILE PICKER ----------------
def load_custom_level_pyqt():
    app = QApplication.instance()
    if not app:
        app = QApplication([])

    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select Level File",
        "levels",
        "JSON Files (*.json)",
        options=options
    )
    return file_path or None

# ---------------- RUN LEVEL ----------------
def run_level(level_num=None, custom_path=None):
    if custom_path:
        level_path = custom_path
    else:
        level_path = f"levels/level{level_num}.json"
        if not os.path.exists(level_path):
            return

    maze = Maze(level_path)
    player = Player(maze.player_start)

    # spawn all monsters
    monsters = [Monster(color, pos) for color, pos in maze.monsters_info]

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    pygame.mouse.get_rel()

    while True:
        dt = clock.tick(FPS) / 1000

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    return
                if e.key == pygame.K_F11:
                    toggle_fullscreen()

        mx, _ = pygame.mouse.get_rel()
        player.angle += mx * 0.002

        # movement
        keys = pygame.key.get_pressed()
        speed = PLAYER_WALK_SPEED
        if keys[pygame.K_LSHIFT] and player.stamina > 0:
            speed = PLAYER_RUN_SPEED
            player.stamina -= STAMINA_DRAIN * dt
        else:
            player.stamina += STAMINA_REGEN * dt
        player.stamina = max(0, min(STAMINA_MAX, player.stamina))

        dx = math.cos(player.angle) * speed * dt
        dy = math.sin(player.angle) * speed * dt
        if keys[pygame.K_w]: player.move(dx, dy, maze)
        if keys[pygame.K_s]: player.move(-dx, -dy, maze)
        if keys[pygame.K_a]: player.move(dy, -dx, maze)
        if keys[pygame.K_d]: player.move(-dy, dx, maze)

        # monster logic
        for monster in monsters:
            angle_to_monster = math.atan2(monster.y - player.y, monster.x - player.x)
            angle_diff = (angle_to_monster - player.angle + math.pi) % math.tau - math.pi
            looking_at_monster = abs(angle_diff) < FOV / 6
            monster.update(player, maze, looking_at_monster)

        # render
        screen.fill((15,15,15))
        render(screen, player, maze, monsters)

        # overlay if spotted
        for monster in monsters:
            if monster.can_see_player(player, maze):
                overlay(screen, {"red":(255,0,0),"blue":(0,0,255),"green":(0,255,0)}[monster.color])

        # compass
        maze.check_compass_pickup(player.x, player.y)
        angle = maze.compass_angle(player.x, player.y)
        if angle is not None:
            cx, cy = screen.get_width()//2, screen.get_height()-40
            pygame.draw.circle(screen, (60,60,60), (cx,cy), 22)
            rel = angle - player.angle
            ax = cx + int(math.sin(rel)*14)
            ay = cy - int(math.cos(rel)*14)
            pygame.draw.line(screen,(255,255,0),(cx,cy),(ax,ay),3)

        # fake exit
        if maze.reached_fake_exit(player.x, player.y):
            overlay(screen,(120,0,120))
            player.x, player.y = maze.player_start

        # caught
        for monster in monsters:
            if monster.caught_player(player):
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
                choice = game_over_screen(screen)
                if choice == "Restart":
                    return run_level(level_num, custom_path)
                elif choice == "Back to Menu":
                    return
                else:
                    pygame.quit()
                    sys.exit()

        # real exit
        if maze.reached_real_exit(player.x, player.y):
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            choice = win_screen(screen)
            if choice == "Back to Menu":
                return
            else:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

# ---------------- MENU ----------------
def menu():
    font = pygame.font.SysFont(None,48)
    while True:
        screen.fill((0,0,0))
        title = font.render("MAZE HORROR", True, (200,0,0))
        screen.blit(title,(WIDTH//2-title.get_width()//2,120))

        options = [
            "1 - Level 1",
            "2 - Level 2",
            "3 - Level 3",
            "L - Load Custom Level",
            "ESC - Quit"
        ]
        for i,opt in enumerate(options):
            text = font.render(opt, True, (255,255,255))
            screen.blit(text,(WIDTH//2-250,220+i*50))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: run_level(1)
                if e.key == pygame.K_2: run_level(2)
                if e.key == pygame.K_3: run_level(3)
                if e.key == pygame.K_l:
                    path = load_custom_level_pyqt()
                    if path: run_level(custom_path=path)
                if e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

# ---------------- START ----------------
menu()