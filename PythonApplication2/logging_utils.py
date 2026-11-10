# logging_utils.py
# Lab 2. Wave logging and CSV tables (spec sections 3-5)
import csv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


def _ensure_output():
    OUTPUT_DIR.mkdir(exist_ok=True)


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------- 1. log_defense.txt ----------
LOG_PATH = OUTPUT_DIR / "log_defense.txt"


def log_wave(wave_no, spawned, killed, leaked,
             gold_earned, gold_spent, towers_online):
    _ensure_output()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{_ts()}] WAVE {wave_no}: spawned={spawned} killed={killed} "
                f"leaked={leaked} gold_earned={gold_earned} "
                f"gold_spent={gold_spent} towers_online={towers_online}\n")


def log_final(result, player, waves_passed):
    _ensure_output()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{_ts()}] SESSION END: player={player} "
                f"waves_passed={waves_passed} result={result}\n")


# ---------- 2. towers_built.csv ----------
TOWERS_CSV = OUTPUT_DIR / "towers_built.csv"
TOWERS_HEADER = ["tower_type", "x", "y", "wave_built",
                 "total_damage", "kills", "connected"]


def _init_towers_csv():
    _ensure_output()
    if not TOWERS_CSV.exists():
        with open(TOWERS_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(TOWERS_HEADER)


def append_tower_row(tower_type, x, y, wave_built,
                     total_damage, kills, connected):
    _init_towers_csv()
    with open(TOWERS_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([tower_type, x, y, wave_built,
                                total_damage, kills, int(bool(connected))])


# ---------- 3. defense_stats.csv ----------
STATS_CSV = OUTPUT_DIR / "defense_stats.csv"
STATS_HEADER = ["player", "waves_passed", "total_kills",
                "total_gold_earned", "result"]


def _init_stats_csv():
    _ensure_output()
    if not STATS_CSV.exists():
        with open(STATS_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(STATS_HEADER)


def append_session_stats(player, waves_passed, total_kills,
                         total_gold_earned, result):
    _init_stats_csv()
    with open(STATS_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([player, waves_passed, total_kills,
                                total_gold_earned, result])