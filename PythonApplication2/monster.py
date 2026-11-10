# monster.py
# Monster class. Moves along a list of path waypoints.

import math
import pygame
from constants import (
    MONSTER_BASE_HP, MONSTER_BASE_SPEED,
    MONSTER_RADIUS, COLORS,
    BOSS_HP_MULTIPLIER, BOSS_SPEED_MULTIPLIER,
    BOSS_RADIUS,
)
from level import PATH_POINTS


class Monster:
    """A monster walking along the path from the first point to the last."""

    def __init__(self, hp_multiplier=1.0, speed_multiplier=1.0,
                 is_boss=False, stats=None):
        self.x, self.y = PATH_POINTS[0]
        self.path_index = 1
        self.is_boss = is_boss

        # Если передан stats из balance_cfg — используем его
        if stats is None:
            stats = {
                "hp": MONSTER_BASE_HP,
                "speed": MONSTER_BASE_SPEED,
                "radius": BOSS_RADIUS if is_boss else MONSTER_RADIUS,
                "reward": 30 if is_boss else 7,
                "leak_penalty": 3 if is_boss else 1,
            }

        base_hp = stats["hp"] * hp_multiplier
        if is_boss:
            base_hp *= BOSS_HP_MULTIPLIER
        self.max_hp = int(base_hp)
        self.hp = self.max_hp

        base_speed = stats["speed"] * speed_multiplier
        if is_boss:
            base_speed *= BOSS_SPEED_MULTIPLIER
        self.speed = base_speed

        self.radius = BOSS_RADIUS if is_boss else stats.get("radius", MONSTER_RADIUS)
        self.reward = stats.get("reward", 7)
        self.leak_penalty = stats.get("leak_penalty", 1)
        self.alive = True
        self.reached_end = False

    # --- Logic ---
    def update(self, dt):
        """Smooth movement from one waypoint to the next."""
        if not self.alive:
            return
        if self.path_index >= len(PATH_POINTS):
            self.reached_end = True
            return

        tx, ty = PATH_POINTS[self.path_index]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        if dist < 1e-3:
            self.path_index += 1
            return

        step = self.speed * dt
        if step >= dist:
            self.x, self.y = tx, ty
            self.path_index += 1
        else:
            self.x += dx / dist * step
            self.y += dy / dist * step

    def take_damage(self, amount):
        """Reduces HP. Returns True if the monster dies."""
        if not self.alive:
            return False
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return True
        return False

    # --- Rendering ---
    def draw(self, surface, font):
        if not self.alive:
            return

        if self.is_boss:
            # Boss: dark red body with a bright outline
            pygame.draw.circle(surface, (140, 30, 30),
                               (int(self.x), int(self.y)),
                               int(self.radius))
            pygame.draw.circle(surface, (255, 200, 60),
                               (int(self.x), int(self.y)),
                               int(self.radius), 3)
            # Small crown-like marker
            pygame.draw.circle(surface, (255, 230, 100),
                               (int(self.x), int(self.y - self.radius - 6)),
                               4)
        else:
            pygame.draw.circle(surface, COLORS["monster"],
                               (int(self.x), int(self.y)),
                               int(self.radius))

        # HP bar (wider for bosses)
        bar_w = 40 if self.is_boss else 26
        bar_h = 5 if self.is_boss else 4
        bx = int(self.x - bar_w / 2)
        by = int(self.y - self.radius - 10)
        ratio = self.hp / self.max_hp if self.max_hp > 0 else 0
        pygame.draw.rect(surface, (60, 60, 60), (bx, by, bar_w, bar_h))
        bar_color = (255, 120, 60) if self.is_boss else COLORS["monster_hp"]
        pygame.draw.rect(surface, bar_color,
                         (bx, by, int(bar_w * ratio), bar_h))