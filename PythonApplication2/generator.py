# generator.py
# Main generator - the source of energy.

import pygame
from constants import TILE_SIZE, COLORS


class Generator:
    """Main generator. All towers must be connected to it."""

    def __init__(self, gx, gy):
        self.gx = gx
        self.gy = gy
        self.x = gx * TILE_SIZE + TILE_SIZE // 2
        self.y = gy * TILE_SIZE + TILE_SIZE // 2
        self.powered = True

    def set_powered(self, value):
        """Sets powered state (for API symmetry with Tower)."""
        self.powered = value

    def draw(self, surface, font, pulse):
        """Renders the generator with a pulsating glow."""
        glow_r = int(TILE_SIZE // 2 + 6 + pulse)
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (250, 200, 60, 60),
                           (glow_r, glow_r), glow_r)
        surface.blit(glow, (self.x - glow_r, self.y - glow_r))

        rect = pygame.Rect(self.gx * TILE_SIZE + 4,
                           self.gy * TILE_SIZE + 4,
                           TILE_SIZE - 8, TILE_SIZE - 8)
        pygame.draw.rect(surface, COLORS["generator"], rect, border_radius=8)
        pygame.draw.rect(surface, (120, 90, 20), rect, 3, border_radius=8)

        label = font.render("G", True, (60, 40, 0))
        surface.blit(label, (self.x - label.get_width() // 2,
                             self.y - label.get_height() // 2))