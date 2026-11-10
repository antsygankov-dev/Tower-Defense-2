# constants.py
# All project constants are stored in a separate module (Lab 1 requirement).

# --- Window size ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# --- Grid ---
TILE_SIZE = 40
GRID_COLUMNS = WINDOW_WIDTH // TILE_SIZE   # 20
GRID_ROWS = WINDOW_HEIGHT // TILE_SIZE     # 15

# --- FPS ---
FPS = 60

# --- Colors ---
COLORS = {
    "bg":         (28, 32, 38),
    "grid":       (45, 52, 60),
    "path":       (120, 100, 70),
    "path_edge":  (160, 140, 100),
    "tower":      (60, 160, 220),
    "tower_off":  (110, 110, 120),
    "generator":  (250, 200, 60),
    "monster":    (220, 70, 70),
    "monster_hp": (120, 240, 120),
    "line":       (255, 230, 120),
    "text":       (240, 240, 240),
    "text_dim":   (170, 170, 170),
    "danger":     (240, 90, 90),
    "good":       (90, 220, 120),
}

# --- Economy ---
START_MONEY = 100
START_HP = 10
TOWER_COST = 50
KILL_REWARD = 7
WAVE_REWARD = 20

# --- Tower ---
TOWER_RANGE = 90
TOWER_DAMAGE = 24
TOWER_FIRE_COOLDOWN_MS = 1000

# --- Energy grid ---
ENERGY_RANGE = 170

# --- Monsters ---
MONSTER_BASE_HP = 65
MONSTER_BASE_SPEED = 55
MONSTER_RADIUS = 15

# --- Bosses ---
BOSS_HP_MULTIPLIER = 8.5      
BOSS_SPEED_MULTIPLIER = 0.7   
BOSS_RADIUS = 22              
BOSS_KILL_REWARD = 30         

# --- Game states ---
STATE_MENU = "MENU"
STATE_PLAY = "PLAY"
STATE_OVER = "OVER"
STATE_WIN = "WIN"