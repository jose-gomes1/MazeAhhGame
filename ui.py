import pygame
import sys

def overlay(screen, color):
    surf = pygame.Surface(screen.get_size())
    surf.set_alpha(70)
    surf.fill(color)
    screen.blit(surf, (0, 0))

def game_over_screen(screen):
    return menu_screen(screen, "GAME OVER", (200, 0, 0))

def win_screen(screen):
    return menu_screen(screen, "YAY, YOU WON!", (0, 200, 0))

def menu_screen(screen, title_text, title_color):
    font_big = pygame.font.SysFont(None, 72)
    font = pygame.font.SysFont(None, 40)

    options = ["Back to Menu", "Quit Game"]
    selected = 0

    while True:
        screen.fill((0, 0, 0))

        title = font_big.render(title_text, True, title_color)
        screen.blit(
            title,
            (screen.get_width() // 2 - title.get_width() // 2, 120)
        )

        for i, opt in enumerate(options):
            color = (255, 255, 255) if i == selected else (120, 120, 120)
            text = font.render(opt, True, color)
            screen.blit(
                text,
                (screen.get_width() // 2 - 120, 260 + i * 60)
            )

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if e.key == pygame.K_RETURN:
                    return options[selected]