# main.py
# Entry point. Game loop, event handling, update, rendering.

import sys
import math
import pygame

from config_loader import load_all
level_cfg, balance_cfg = load_all()
print("TEST: level =", level_cfg["level_name"])
print("TEST: monsters =", list(balance_cfg["monsters"].keys()))

from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TILE_SIZE,
    COLORS, START_MONEY, START_HP, TOWER_COST, KILL_REWARD,
    WAVE_REWARD, BOSS_KILL_REWARD,
    STATE_MENU, STATE_PLAY, STATE_OVER, STATE_WIN,
)
from level import (
    PATH_POINTS, is_path_tile, is_inside_grid, pixel_to_tile,
)
from monster import Monster
from tower import Tower
from generator import Generator
from energy_network import compute_powered_towers, draw_energy_lines
from hud import draw_menu, draw_hud, draw_game_over, draw_text


# --- Wave parameters ---
MAX_WAVES = 15
# (count, hp_multiplier, speed_multiplier, interval_ms)
WAVES = [
    (3,  1.0,  1.0,  1000),   # 1
    (5,  1.1,  1.02, 900),    # 2
    (7,  1.2,  1.04, 850),    # 3
    (9,  1.35, 1.06, 800),    # 4
    (6,  1.6,  1.08, 900),    # 5 - BOSS
    (11, 1.7,  1.10, 750),    # 6
    (13, 1.85, 1.12, 720),    # 7
    (15, 2.0,  1.14, 700),    # 8
    (17, 2.2,  1.16, 680),    # 9
    (8,  2.6,  1.18, 900),    # 10 - BOSS
    (19, 2.9,  1.20, 650),    # 11
    (22, 3.2,  1.22, 620),    # 12
    (25, 3.5,  1.24, 600),    # 13
    (28, 3.8,  1.26, 580),    # 14
    (10, 4.5,  1.28, 900),    # 15 - FINAL BOSS
]

# Indexes (0-based) of waves that contain a boss as their last spawn.
BOSS_WAVES = {4, 9, 14}


class Game:
    """Main game class."""

    def __init__(self, screen, font, big_font):
        self.screen = screen
        self.font = font
        self.big_font = big_font
        self.state = STATE_MENU
        self.reset()

    # --- Reset ---
    def reset(self):
        self.money = START_MONEY
        self.hp = START_HP
        self.wave_index = 0
        self.wave_timer = 0
        self.spawned_in_wave = 0
        self.wave_active = False
        self.monsters = []
        self.towers = []
        self.generator = Generator(10, 6)
        self.pulse = 0.0
        self.messages = []
        self.powered_towers = []
        self.energy_edges = []

    # --- Controls ---
    def start_game(self):
        self.reset()
        self.state = STATE_PLAY
        self.start_wave(0)

    def start_wave(self, index):
        self.wave_index = index
        self.wave_active = True
        self.spawned_in_wave = 0
        self.wave_timer = pygame.time.get_ticks()
        if index in BOSS_WAVES:
            self.add_message(f"WAVE {index + 1}: BOSS INCOMING!")

    # --- Event handling ---
    def handle_event(self, event):
        if self.state == STATE_MENU:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.start_game()
            return

        if self.state in (STATE_OVER, STATE_WIN):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.state = STATE_MENU
            return

        if self.state == STATE_PLAY:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                gx, gy = pixel_to_tile(mx, my)
                if not is_inside_grid(gx, gy):
                    return
                if event.button == 1:
                    self.try_build_tower(gx, gy)
                elif event.button == 3:
                    self.try_remove_tower(gx, gy)

    def try_build_tower(self, gx, gy):
        if is_path_tile(gx, gy):
            self.add_message("You cannot build on the path.")
            return
        if (gx, gy) == (self.generator.gx, self.generator.gy):
            self.add_message("Here is the generator.")
            return
        for t in self.towers:
            if (t.gx, t.gy) == (gx, gy):
                self.add_message("Tile is busy.")
                return
        if self.money < TOWER_COST:
            self.add_message("Insufficient funds")
            return
        self.money -= TOWER_COST
        self.towers.append(Tower(gx, gy))
        self.recompute_energy()

    def try_remove_tower(self, gx, gy):
        for t in self.towers[:]:
            if (t.gx, t.gy) == (gx, gy):
                self.towers.remove(t)
                self.money += TOWER_COST // 2
                self.recompute_energy()
                return

    def add_message(self, text):
        self.messages.append((text, pygame.time.get_ticks()))

    # --- Energy grid ---
    def recompute_energy(self):
        powered, edges = compute_powered_towers(self.generator, self.towers)
        self.powered_towers = powered
        self.energy_edges = edges

    # --- Update ---
    def update(self, dt, now_ms):
        self.pulse = (math.sin(now_ms / 300.0) + 1) * 2

        self.messages = [m for m in self.messages
                         if now_ms - m[1] < 2000]

        if self.state != STATE_PLAY:
            return

        # --- Monster spawn ---
        if self.wave_active and self.wave_index < len(WAVES):
            count, hp_mul, sp_mul, interval = WAVES[self.wave_index]
            total = count + (1 if self.wave_index in BOSS_WAVES else 0)

            if self.spawned_in_wave < total:
                if now_ms - self.wave_timer >= interval:
                    self.wave_timer = now_ms
                    is_boss = (self.wave_index in BOSS_WAVES
                               and self.spawned_in_wave == count)
                    self.spawned_in_wave += 1
                    self.monsters.append(
                        Monster(hp_mul, sp_mul, is_boss=is_boss)
                    )
            else:
                if not any(m.alive for m in self.monsters):
                    self.finish_wave()
                    return

        # --- Update monsters ---
        for m in self.monsters:
            m.update(dt)
            if m.reached_end and m.alive:
                m.alive = False
                self.hp -= 1
                if self.hp <= 0:
                    self.state = STATE_OVER
                    return

        # --- Update towers ---
        for t in self.towers:
            res = t.update(self.monsters, now_ms)
            if res and res["killed"]:
                if res["target"].is_boss:
                    self.money += BOSS_KILL_REWARD
                else:
                    self.money += KILL_REWARD

        # Remove dead monsters
        self.monsters = [m for m in self.monsters if m.alive]

        # --- Defeat check ---
        if self.hp <= 0:
            self.state = STATE_OVER

    def finish_wave(self):
        self.wave_active = False
        self.money += WAVE_REWARD
        self.add_message(
            f"Wave {self.wave_index + 1} completed! +${WAVE_REWARD}"
        )
        if self.wave_index + 1 >= len(WAVES):
            self.state = STATE_WIN
        else:
            self.start_wave(self.wave_index + 1)

    # --- Rendering ---
    def draw(self):
        if self.state == STATE_MENU:
            draw_menu(self.screen, self.big_font, self.font)
            return

        self.screen.fill(COLORS["bg"])
        self.draw_grid()
        self.draw_path()

        draw_energy_lines(self.screen, self.energy_edges, COLORS["line"])

        self.generator.draw(self.screen, self.font, self.pulse)
        for t in self.towers:
            t.draw_range(self.screen)
        for t in self.towers:
            t.draw(self.screen)
        for m in self.monsters:
            m.draw(self.screen, self.font)

        self.draw_preview()

        draw_hud(self.screen, self.font, self.big_font,
                 self.money, self.hp,
                 self.wave_index + 1, len(WAVES),
                 len(self.monsters), len(self.towers),
                 len(self.powered_towers))

        y = 50
        for text, ts in self.messages:
            draw_text(self.screen, text, self.font, 12, y,
                      COLORS["danger"])
            y += 22

        if self.state in (STATE_OVER, STATE_WIN):
            draw_game_over(self.screen, self.big_font, self.font,
                           self.state == STATE_WIN,
                           self.wave_index + 1, len(WAVES))

    def draw_grid(self):
        for gx in range(0, WINDOW_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, COLORS["grid"],
                             (gx, 0), (gx, WINDOW_HEIGHT))
        for gy in range(0, WINDOW_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, COLORS["grid"],
                             (0, gy), (WINDOW_WIDTH, gy))

    def draw_path(self):
        if len(PATH_POINTS) >= 2:
            pygame.draw.lines(self.screen, COLORS["path_edge"],
                              False, PATH_POINTS, TILE_SIZE)
            pygame.draw.lines(self.screen, COLORS["path"],
                              False, PATH_POINTS, TILE_SIZE - 6)

    def draw_preview(self):
        """Semi-transparent preview of the tower under the cursor."""
        mx, my = pygame.mouse.get_pos()
        gx, gy = pixel_to_tile(mx, my)
        if not is_inside_grid(gx, gy):
            return
        if is_path_tile(gx, gy):
            return
        if (gx, gy) == (self.generator.gx, self.generator.gy):
            return
        for t in self.towers:
            if (t.gx, t.gy) == (gx, gy):
                return
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        color = ((60, 160, 220, 90) if self.money >= TOWER_COST
                 else (200, 60, 60, 90))
        pygame.draw.rect(surf, color, (4, 4, TILE_SIZE - 8, TILE_SIZE - 8),
                         border_radius=6)
        self.screen.blit(surf, (gx * TILE_SIZE, gy * TILE_SIZE))


def load_font(size):
    """Tries system fonts that support Cyrillic, then falls back."""
    for name in ("arial", "segoeui", "dejavusans", "tahoma"):
        try:
            return pygame.font.SysFont(name, size)
        except Exception:
            continue
    return pygame.font.Font(None, size)


def main():
    pygame.init()
    pygame.font.init()

    font = load_font(22)
    big_font = load_font(52)

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Towers and Energy - Lab 1")
    clock = pygame.time.Clock()

    game = Game(screen, font, big_font)
    last_time = pygame.time.get_ticks()

    while True:
        now = pygame.time.get_ticks()
        dt = (now - last_time) / 1000.0
        last_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)

        game.update(dt, now)
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()