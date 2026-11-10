# energy_network.py
# Graph connectivity algorithm: Prim's algorithm (MST) from the generator
# through towers, where the distance between them is <= ENERGY_RANGE.

import math

import pygame

from constants import ENERGY_RANGE


def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def compute_powered_towers(generator, towers):
    """
    Builds a Minimum Spanning Tree (MST) of towers connected to the generator,
    using Prim's algorithm, where each edge length is <= ENERGY_RANGE.

    Returns (powered_list, edges):
      powered_list -- list of connected towers
      edges        -- list of (a, b) tuples representing the MST
                      (a is the parent, b is the child)
    """
    if generator is None:
        for t in towers:
            t.set_powered(False)
        return [], []

    powered = []
    edges = []
    connected = {id(generator): generator}    # id -> node
    remaining = list(towers)                  # towers not yet connected

    # Mark all as unpowered first
    for t in towers:
        t.set_powered(False)

    while remaining:
        best_pair = None
        best_dist = ENERGY_RANGE + 1

        # Find the closest pair (connected_node, remaining_tower)
        for t in remaining:
            for node in connected.values():
                d = _dist(node, t)
                if d <= ENERGY_RANGE and d < best_dist:
                    best_dist = d
                    best_pair = (node, t)

        if best_pair is None:
            break   # nothing else can be connected

        parent, child = best_pair
        connected[id(child)] = child
        remaining.remove(child)
        child.set_powered(True)
        powered.append(child)
        edges.append((parent, child))

    return powered, edges


def draw_energy_lines(surface, edges, color):
    """Draws energy lines from a precomputed MST."""
    for a, b in edges:
        pygame.draw.line(surface, color,
                         (a.x, a.y), (b.x, b.y), 2)