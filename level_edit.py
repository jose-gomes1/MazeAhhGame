import pygame
import json

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
    save_rect = pygame.Rect(GRID_WIDTH*TILE_SIZE, SCREEN_HEIGHT - TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, (0,200,0), save_rect)
    txt = font.render("SAVE", True, (0,0,0))
    screen.blit(txt, (GRID_WIDTH*TILE_SIZE + 5, SCREEN_HEIGHT - TILE_SIZE + 10))
    return save_rect

running = True
while running:
    save_rect = draw()
    pygame.display.flip()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = e.pos
            if mx < GRID_WIDTH*TILE_SIZE and my < GRID_HEIGHT*TILE_SIZE:
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                grid[gy][gx] = selected_tile
            elif mx >= GRID_WIDTH*TILE_SIZE:
                # toolbar clicks
                index = my // TILE_SIZE
                if index < len(tiles):
                    selected_tile = tiles[index]
                elif save_rect.collidepoint(e.pos):
                    filename = input("Filename to save (e.g., level1.json): ")
                    with open(filename, "w") as f:
                        json.dump({"map":["".join(r) for r in grid]}, f, indent=2)
                    print("Saved", filename)
pygame.quit()