# config_loader.py
# Lab 2. Parsing and validation of grid_level.json / defense_balances.json
import json
import sys
from pathlib import Path

import constants

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


class ConfigError(Exception):
    pass


def _load_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"File not found: {path}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"Broken JSON in {path}: {e}")


def _default_monster_stats(name: str) -> dict:
    """Fallback stats from constants.py if a field is missing in JSON."""
    if name == "boss":
        return {
            "speed": round(constants.MONSTER_BASE_SPEED * constants.BOSS_SPEED_MULTIPLIER),
            "hp": round(constants.MONSTER_BASE_HP * constants.BOSS_HP_MULTIPLIER),
            "reward": constants.BOSS_KILL_REWARD,
            "leak_penalty": 3,
            "radius": constants.BOSS_RADIUS,
        }
    return {
        "speed": constants.MONSTER_BASE_SPEED,
        "hp": constants.MONSTER_BASE_HP,
        "reward": constants.KILL_REWARD,
        "leak_penalty": 1,
        "radius": constants.MONSTER_RADIUS,
    }


def _default_tower_stats() -> dict:
    return {
        "price": constants.TOWER_COST,
        "damage": constants.TOWER_DAMAGE,
        "radius": constants.TOWER_RANGE,
        "connect_cost": 10,
        "fire_cooldown_ms": constants.TOWER_FIRE_COOLDOWN_MS,
    }


def load_level(path: Path = None) -> dict:
    path = path or DATA_DIR / "grid_level.json"
    data = _load_json(path)

    required = ("path_points", "generator", "start_gold", "base_hp", "grid", "waves")
    for field in required:
        if field not in data:
            raise ConfigError(f"Field '{field}' missing in grid_level.json")

    if not isinstance(data["path_points"], list) or len(data["path_points"]) < 2:
        raise ConfigError("path_points must contain at least 2 points")
    for p in data["path_points"]:
        if not (isinstance(p, list) and len(p) == 2):
            raise ConfigError(f"Invalid waypoint: {p}")

    if data["start_gold"] < 0:
        raise ConfigError("start_gold cannot be negative")
    if data["base_hp"] <= 0:
        raise ConfigError("base_hp must be positive")
    if not data["waves"]:
        raise ConfigError("waves list is empty")

    if data["grid"].get("cell_size", constants.TILE_SIZE) != constants.TILE_SIZE:
        print(f"[CONFIG WARN] grid.cell_size={data['grid']['cell_size']} "
              f"!= constants.TILE_SIZE={constants.TILE_SIZE}", file=sys.stderr)

    return data


def load_balances(path: Path = None) -> dict:
    path = path or DATA_DIR / "defense_balances.json"
    data = _load_json(path)

    for key in ("monsters", "towers"):
        if key not in data:
            raise ConfigError(f"Field '{key}' missing in defense_balances.json")

    for name, stats in data["monsters"].items():
        defaults = _default_monster_stats(name)
        for k, v in defaults.items():
            stats.setdefault(k, v)
        for k in ("speed", "hp", "reward", "leak_penalty"):
            if stats[k] < 0:
                raise ConfigError(f"Monster {name}: {k} < 0")

    for name, stats in data["towers"].items():
        defaults = _default_tower_stats()
        for k, v in defaults.items():
            stats.setdefault(k, v)
        for k in ("price", "damage", "radius", "connect_cost"):
            if stats[k] < 0:
                raise ConfigError(f"Tower {name}: {k} < 0")
        if stats["radius"] <= 0:
            raise ConfigError(f"Tower {name}: radius must be > 0")

    data.setdefault("energy", {})
    data["energy"].setdefault("max_link_distance", constants.ENERGY_RANGE)

    return data


def load_all(level_path: Path = None, balance_path: Path = None):
    """Returns (level_dict, balances_dict). Exits with code 1 on config error."""
    try:
        level = load_level(level_path)
        balances = load_balances(balance_path)
    except ConfigError as e:
        print(f"[CONFIG ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    for i, wave in enumerate(level["waves"]):
        mtype = wave.get("monster")
        if mtype not in balances["monsters"]:
            print(f"[CONFIG ERROR] Wave #{i+1} references unknown "
                  f"monster '{mtype}'", file=sys.stderr)
            sys.exit(1)
        if wave.get("count", 0) <= 0:
            print(f"[CONFIG ERROR] Wave #{i+1}: count <= 0", file=sys.stderr)
            sys.exit(1)

    print(f"[CONFIG OK] Level '{level.get('level_name', '?')}' loaded. "
          f"Monsters: {len(balances['monsters'])}, "
          f"towers: {len(balances['towers'])}")
    return level, balances