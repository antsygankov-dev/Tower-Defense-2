# hud.py
# Helper functions for drawing the user interface.

import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS


def draw_text(surface, text, font, x, y, color=None):
    color = color or COLORS["text"]
    surf = font.render(text, True, color)
    surface.blit(surf, (x, y))
    return surf.get_width(), surf.get_height()


def draw_hud(surface, font, big_font, money, hp, wave, max_wave,
             monsters_alive, towers_count, powered_count):
    """HUD: money, lives, wave, monsters, power grid."""
    bar = pygame.Surface((WINDOW_WIDTH, 34), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 140))
    surface.blit(bar, (0, 0))

    x = 12
    w, _ = draw_text(surface, f"$ {money}", font, x, 8, COLORS["generator"])
    x += w + 24
    w, _ = draw_text(surface, f"HP: {hp}", font, x, 8, COLORS["danger"])
    x += w + 24
    w, _ = draw_text(surface, f"Wave: {wave}/{max_wave}", font, x, 8)
    x += w + 24
    w, _ = draw_text(surface, f"Monsters: {monsters_alive}", font, x, 8)
    x += w + 24
    draw_text(surface, f"Towers: {powered_count}/{towers_count}",
              font, x, 8, COLORS["good"])

    draw_text(surface, "LMB - place turret ($50)",
              font, 12, WINDOW_HEIGHT - 24, COLORS["text_dim"])


def draw_menu(surface, big_font, font):
    surface.fill(COLORS["bg"])

    title = "TOWERS AND ENERGY"
    w, _ = big_font.size(title)
    draw_text(surface, title, big_font,
              WINDOW_WIDTH // 2 - w // 2, 160, COLORS["generator"])

    lines = [
        "Co-op defense: towers are powered by a generator.",
        "",
        "LMB - place a tower on a free tile",
        "RMB - remove a tower",
        "The tower fires only if connected to a generator,",
        "or with another powered tower (line <= 140 px)",
        "",
        "Press ENTER to start",
    ]
    y = 260
    for line in lines:
        draw_text(surface, line, font, 90, y, COLORS["text_dim"])
        y += 26


def draw_game_over(surface, big_font, font, win, wave, max_wave):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    title = "VICTORY!" if win else "DEFEAT"
    color = COLORS["good"] if win else COLORS["danger"]
    w, _ = big_font.size(title)
    draw_text(surface, title, big_font,
              WINDOW_WIDTH // 2 - w // 2, 220, color)

    msg = f"Waves completed: {wave}/{max_wave}"
    w, _ = font.size(msg)
    draw_text(surface, msg, font,
              WINDOW_WIDTH // 2 - w // 2, 320, COLORS["text"])

    msg = "ENTER - to menu"
    w, _ = font.size(msg)
    draw_text(surface, msg, font,
              WINDOW_WIDTH // 2 - w // 2, 380, COLORS["text_dim"])