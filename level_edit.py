import pygame
import json
import os
import copy

# ---------------- SETTINGS ----------------
TILE_SIZE = 40
GRID_WIDTH = 15
GRID_HEIGHT = 10
TOOL_WIDTH = 120
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH + TOOL_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level Editor")
font = pygame.font.SysFont(None, 24)

# ---------------- GRID ----------------
grid = [["." for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

tiles = ["#", ".", "P", "M", "E", "F", "C"]
colors = {
    "#": (100, 100, 100),
    ".": (30, 30, 30),
    "P": (0, 255, 0),
    "M": (255, 0, 0),
    "E": (0, 0, 0),
    "F": (60, 60, 60),
    "C": (70, 70, 70)
}

selected_tile = tiles[0]

# ---------------- UNDO / REDO ----------------
undo_stack = []
redo_stack = []

def copy_grid():
    return copy.deepcopy(grid)

# ---------------- SAVE SYSTEM ----------------
current_filename = None

def save_level(name):
    global current_filename

    if not name.endswith(".json"):
        name += ".json"

    if not os.path.exists("levels"):
        os.makedirs("levels")

    path = os.path.join("levels", name)

    with open(path, "w") as f:
        json.dump({"map": ["".join(r) for r in grid]}, f, indent=2)

    current_filename = name
    print("Saved to", path)

# ---------------- DRAW ----------------
def draw():
    screen.fill((50, 50, 50))

    # Draw grid
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, colors[grid[y][x]], rect)
            pygame.draw.rect(screen, (0,0,0), rect, 1)

    # Draw toolbar
    for i, t in enumerate(tiles):
        rect = pygame.Rect(GRID_WIDTH*TILE_SIZE, i*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, colors[t], rect)

        if t == selected_tile:
            pygame.draw.rect(screen, (255,255,0), rect, 3)

        text = font.render(t, True, (255,255,255))
        screen.blit(text, (GRID_WIDTH*TILE_SIZE + 5, i*TILE_SIZE + 5))

    # Save button
    save_rect = pygame.Rect(
        GRID_WIDTH*TILE_SIZE,
        SCREEN_HEIGHT - TILE_SIZE,
        TILE_SIZE,
        TILE_SIZE
    )
    pygame.draw.rect(screen, (0,200,0), save_rect)
    txt = font.render("SAVE", True, (0,0,0))
    screen.blit(txt, (GRID_WIDTH*TILE_SIZE + 5, SCREEN_HEIGHT - TILE_SIZE + 10))

    return save_rect

# ---------------- MAIN LOOP ----------------
running = True
painting = False
erasing = False

while running:
    save_rect = draw()
    pygame.display.flip()

    for e in pygame.event.get():

        # Quit
        if e.type == pygame.QUIT:
            running = False

        # ---------------- KEY CONTROLS ----------------
        if e.type == pygame.KEYDOWN:
            if e.mod & pygame.KMOD_CTRL:

                # UNDO
                if e.key == pygame.K_z and undo_stack:
                    redo_stack.append(copy_grid())
                    grid[:] = undo_stack.pop()

                # REDO
                if e.key == pygame.K_y and redo_stack:
                    undo_stack.append(copy_grid())
                    grid[:] = redo_stack.pop()

        # ---------------- MOUSE DOWN ----------------
        if e.type == pygame.MOUSEBUTTONDOWN:

            mx, my = e.pos

            # LEFT CLICK = PAINT
            if e.button == 1:
                if mx < GRID_WIDTH*TILE_SIZE and my < GRID_HEIGHT*TILE_SIZE:
                    painting = True
                    undo_stack.append(copy_grid())
                    redo_stack.clear()

                    gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                    grid[gy][gx] = selected_tile

                elif mx >= GRID_WIDTH*TILE_SIZE:
                    index = my // TILE_SIZE

                    if index < len(tiles):
                        selected_tile = tiles[index]

                    elif save_rect.collidepoint(e.pos):
                        if not current_filename:
                            name = input("Level name: ")
                        else:
                            name = current_filename.replace(".json", "")

                        save_level(name)

            # RIGHT CLICK = ERASE
            if e.button == 3:
                if mx < GRID_WIDTH*TILE_SIZE and my < GRID_HEIGHT*TILE_SIZE:
                    erasing = True
                    undo_stack.append(copy_grid())
                    redo_stack.clear()

                    gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                    grid[gy][gx] = "."

        # ---------------- MOUSE UP ----------------
        if e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1:
                painting = False
            if e.button == 3:
                erasing = False

        # ---------------- DRAG ----------------
        if e.type == pygame.MOUSEMOTION:
            mx, my = e.pos

            # Drag paint
            if painting:
                if mx < GRID_WIDTH*TILE_SIZE and my < GRID_HEIGHT*TILE_SIZE:
                    gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                    grid[gy][gx] = selected_tile

            # Drag erase
            if erasing:
                if mx < GRID_WIDTH*TILE_SIZE and my < GRID_HEIGHT*TILE_SIZE:
                    gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                    grid[gy][gx] = "."

pygame.quit()