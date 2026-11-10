# level.py
# Path description and helper functions.

from constants import TILE_SIZE, GRID_COLUMNS, GRID_ROWS
from config_loader import load_all

# Load level config to get path points
level_cfg, _ = load_all()

# Path is defined by a list of waypoints (in pixels, tile centers).
PATH_POINTS = [tuple(p) for p in level_cfg["path_points"]]

# Tiles occupied by the path (towers cannot be placed here).
PATH_TILES = set()


def _mark_path_tiles():
    """Marks the tiles that the path passes through."""
    for i in range(len(PATH_POINTS) - 1):
        x1, y1 = PATH_POINTS[i]
        x2, y2 = PATH_POINTS[i + 1]

        if x1 == x2:                       # vertical segment
            step = TILE_SIZE if y2 > y1 else -TILE_SIZE
            for y in range(y1, y2 + (step if step > 0 else -1), step):
                PATH_TILES.add((x1 // TILE_SIZE, y // TILE_SIZE))

        elif y1 == y2:                     # horizontal segment
            step = TILE_SIZE if x2 > x1 else -TILE_SIZE
            for x in range(x1, x2 + (step if step > 0 else -1), step):
                PATH_TILES.add((x // TILE_SIZE, y1 // TILE_SIZE))


_mark_path_tiles()


def is_path_tile(gx, gy):
    """Checks whether the tile is occupied by a path."""
    return (gx, gy) in PATH_TILES


def is_inside_grid(gx, gy):
    """Checks whether the tile is within the game board."""
    return 0 <= gx < GRID_COLUMNS and 0 <= gy < GRID_ROWS


def tile_center(gx, gy):
    """Returns the pixel center of the tile."""
    return gx * TILE_SIZE + TILE_SIZE // 2, gy * TILE_SIZE + TILE_SIZE // 2


def pixel_to_tile(px, py):
    """Converts pixel coordinates to grid coordinates."""
    return px // TILE_SIZE, py // TILE_SIZE