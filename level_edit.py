import pygame
import json
import os
import copy

# ---------------- SETTINGS ----------------
TILE_SIZE = 40
GRID_WIDTH = 15
GRID_HEIGHT = 10
TOOL_WIDTH = 200
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH + TOOL_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level Editor")
font = pygame.font.SysFont(None, 24)

# ---------------- GRID ----------------
grid = [["." for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Base tiles (toolbar)
tiles = ["#", ".", "P", "E", "F", "C", "M"]

colors = {
    "#": (100, 100, 100),   # Wall
    ".": (30, 30, 30),     # Empty
    "P": (0, 255, 0),      # Player
    "E": (255, 255, 0),    # Exit
    "F": (200, 150, 0),    # Fake Exit
    "C": (0, 255, 255),    # Compass
    "R": (255, 0, 0),      # Red Monster
    "B": (0, 100, 255),    # Blue Monster
    "G": (0, 255, 100)     # Green Monster
}

selected_tile = "#"

# ---------------- MONSTER TYPES ----------------
monster_types = ["red", "blue", "green"]
monster_index = 0

def get_monster_letter():
    return {
        "red": "R",
        "blue": "B",
        "green": "G"
    }[monster_types[monster_index]]

# ---------------- UNDO / REDO ----------------
undo_stack = []
redo_stack = []

def copy_grid():
    return copy.deepcopy(grid)

# ---------------- SAVE SYSTEM ----------------
saving = False
save_text = ""

def save_level(name):
    if not name.endswith(".json"):
        name += ".json"

    if not os.path.exists("levels"):
        os.makedirs("levels")

    path = os.path.join("levels", name)

    with open(path, "w") as f:
        json.dump({"map": ["".join(r) for r in grid]}, f, indent=2)

    print("Saved to", path)

# ---------------- DRAW ----------------
def draw():
    screen.fill((50, 50, 50))

    # Draw grid
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile = grid[y][x]
            color = colors.get(tile, (30, 30, 30))
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0,0,0), rect, 1)

    # Toolbar
    for i, t in enumerate(tiles):
        rect = pygame.Rect(GRID_WIDTH*TILE_SIZE, i*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, (120,120,120), rect)

        if t == selected_tile:
            pygame.draw.rect(screen, (255,255,0), rect, 3)

        text = font.render(t, True, (255,255,255))
        screen.blit(text, (GRID_WIDTH*TILE_SIZE + 5, i*TILE_SIZE + 5))

    # Monster selector info
    m_text = font.render(f"Monster Type: {monster_types[monster_index]}", True, (255,255,255))
    screen.blit(m_text, (GRID_WIDTH*TILE_SIZE + 5, 300))

    hint1 = font.render("TAB = Change Monster", True, (200,200,200))
    hint2 = font.render("S = Save", True, (200,200,200))
    screen.blit(hint1, (GRID_WIDTH*TILE_SIZE + 5, 330))
    screen.blit(hint2, (GRID_WIDTH*TILE_SIZE + 5, 350))

    # Save input box
    if saving:
        pygame.draw.rect(screen, (0,0,0), (100, SCREEN_HEIGHT//2-20, 400, 40))
        pygame.draw.rect(screen, (255,255,255), (100, SCREEN_HEIGHT//2-20, 400, 40), 2)
        txt = font.render("Save as: " + save_text, True, (255,255,255))
        screen.blit(txt, (110, SCREEN_HEIGHT//2-10))

# ---------------- MAIN LOOP ----------------
running = True
painting = False
erasing = False

while running:
    draw()
    pygame.display.flip()

    for e in pygame.event.get():

        if e.type == pygame.QUIT:
            running = False

        # ---------------- KEYBOARD ----------------
        if e.type == pygame.KEYDOWN:

            if saving:
                if e.key == pygame.K_RETURN:
                    save_level(save_text)
                    save_text = ""
                    saving = False
                elif e.key == pygame.K_BACKSPACE:
                    save_text = save_text[:-1]
                else:
                    save_text += e.unicode
                continue

            if e.mod & pygame.KMOD_CTRL:
                if e.key == pygame.K_z and undo_stack:
                    redo_stack.append(copy_grid())
                    grid[:] = undo_stack.pop()
                if e.key == pygame.K_y and redo_stack:
                    undo_stack.append(copy_grid())
                    grid[:] = redo_stack.pop()

            if e.key == pygame.K_s:
                saving = True

            if e.key == pygame.K_TAB:
                monster_index = (monster_index + 1) % len(monster_types)

        # ---------------- MOUSE ----------------
        if e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = e.pos

            if mx < GRID_WIDTH*TILE_SIZE and my < GRID_HEIGHT*TILE_SIZE:
                undo_stack.append(copy_grid())
                redo_stack.clear()

                gx, gy = mx // TILE_SIZE, my // TILE_SIZE

                if e.button == 1:
                    if selected_tile == "M":
                        grid[gy][gx] = get_monster_letter()
                    else:
                        grid[gy][gx] = selected_tile
                    painting = True

                if e.button == 3:
                    grid[gy][gx] = "."
                    erasing = True

            elif mx >= GRID_WIDTH*TILE_SIZE:
                index = my // TILE_SIZE
                if index < len(tiles):
                    selected_tile = tiles[index]

        if e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1:
                painting = False
            if e.button == 3:
                erasing = False

        if e.type == pygame.MOUSEMOTION:
            mx, my = e.pos
            if mx < GRID_WIDTH*TILE_SIZE and my < GRID_HEIGHT*TILE_SIZE:
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE

                if painting:
                    if selected_tile == "M":
                        grid[gy][gx] = get_monster_letter()
                    else:
                        grid[gy][gx] = selected_tile

                if erasing:
                    grid[gy][gx] = "."

pygame.quit()