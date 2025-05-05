
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import os
import re

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
from ortools.sat.python import cp_model

import io
from PIL import Image


@dataclass
class TilingConfig:
    # --- basic parameters ---
    formats: Dict[int, Tuple[int, int]]
    weights: Dict[int, int]
    grid_size: int
    max_time_in_seconds: float = 60
    num_search_workers: int = 16

    # --- constraint toggles ---
    min_counts: Dict[int, int] = field(default_factory=dict)
    max_counts: Dict[int, int] = field(default_factory=dict)
    enforce_wrap: bool = True
    enforce_no_straight_lines: bool = True
    four_corner_penalty_weight: Optional[int] = 50

def solve_torus_tiling(width_cm: int,
                       height_cm: int,
                       cfg: TilingConfig):
    # 1) validation
    G = cfg.grid_size
    assert width_cm % G == 0 and height_cm % G == 0, \
        f"Floor dims must be multiples of {G}"
    W, H = width_cm // G, height_cm // G

    model = cp_model.CpModel()

    # 2)
    tile_cells = {
        k: [(w//G, h//G), (h//G, w//G)]
        for k,(w,h) in cfg.formats.items()
    }

    # 3) variables X[k,i,j,o]
    X = {}
    for k in cfg.formats:
        for o,(wc,hc) in enumerate(tile_cells[k]):
            for i in range(W):
                for j in range(H):
                    X[k,i,j,o] = model.NewBoolVar(f"X_{k}_{i}_{j}_{o}")

    # 4) coverage
    for x in range(W):
        for y in range(H):
            model.Add(
                sum(
                    X[k,i,j,o]
                    for k in cfg.formats
                    for o,(wc,hc) in enumerate(tile_cells[k])
                    for i in range(W)
                    for j in range(H)
                    if ((x-i)%W) < wc and ((y-j)%H) < hc
                ) == 1
            )

    # 5) min/max counts
    for k in cfg.formats:
        min_c = cfg.min_counts.get(k, 0)
        max_c = cfg.max_counts.get(k, W*H*2)  # sufitowe
        expr = sum(X[k,i,j,o] for i in range(W) for j in range(H) for o in [0,1])
        if min_c > 0:
            model.Add(expr >= min_c)
        if max_c is not None:
            model.Add(expr <= max_c)

    # 6)
    if cfg.enforce_wrap:
        model.Add(
            sum(X[k,i,j,o]
                for k in cfg.formats
                for o,(wc,hc) in enumerate(tile_cells[k])
                for i in range(W) for j in range(H)
                if j+hc > H) >= 1
        )
        model.Add(
            sum(X[k,i,j,o]
                for k in cfg.formats
                for o,(wc,hc) in enumerate(tile_cells[k])
                for i in range(W) for j in range(H)
                if i+wc > W) >= 1
        )

    # 7)
    if cfg.enforce_no_straight_lines:
        for b in range(W):
            model.Add(
                sum(X[k,i,j,o]
                    for k in cfg.formats
                    for o,(wc,_) in enumerate(tile_cells[k])
                    for i in range(W) for j in range(H)
                    if 0 < ((b-i)%W) < wc) >= 1
            )
        for r in range(H):
            model.Add(
                sum(X[k,i,j,o]
                    for k in cfg.formats
                    for o,(_,hc) in enumerate(tile_cells[k])
                    for i in range(W) for j in range(H)
                    if 0 < ((r-j)%H) < hc) >= 1
            )

    # 8)
    C = {}
    if cfg.four_corner_penalty_weight is not None:
        for b in range(W):
            for r in range(H):
                C[b,r] = model.NewBoolVar(f"C_{b}_{r}")
                corners = []
                for k in cfg.formats:
                    for o,(wc,hc) in enumerate(tile_cells[k]):
                        for i in range(W):
                            for j in range(H):
                                if ((i%W)==b and (j%H)==r) or \
                                   ((i+wc)%W==b and (j%H)==r) or \
                                   ((i%W)==b and (j+hc)%H==r) or \
                                   ((i+wc)%W==b and (j+hc)%H==r):
                                    corners.append(X[k,i,j,o])
                model.Add(sum(corners)==4).OnlyEnforceIf(C[b,r])
                model.Add(sum(corners)<=3).OnlyEnforceIf(C[b,r].Not())

    # 9)
    obj_terms = []
    for k,w in cfg.weights.items():
        obj_terms.append(
            w * sum(X[k,i,j,o] for i in range(W) for j in range(H) for o in [0,1])
        )
    if cfg.four_corner_penalty_weight is not None:
        obj_terms.append(cfg.four_corner_penalty_weight * sum(C.values()))

    model.Minimize(sum(obj_terms))

    # 10) solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = cfg.max_time_in_seconds
    solver.parameters.num_search_workers = cfg.num_search_workers
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    placements = [(k,i,j,o) for (k,i,j,o),v in X.items() if solver.Value(v)]
    return placements, width_cm, height_cm, G



def draw_tiling(placements, width_cm: int, height_cm: int, G: int,
                formats: Dict[int, Tuple[int,int]]):
    # Recompute tile_cells for drawing
    tile_cells = {
        k: [(w // G, h // G), (h // G, w // G)]
        for k, (w, h) in formats.items()
    }

    fig, ax = plt.subplots()
    # Colors for central block and neighbors
    # Colors for central block (strong red) and neighbors (weak red)
    central_colors = {}
    neighbor_colors = {}
    for k in formats:
        g = random.random()
        b = random.random()
        # strong red component > 0.5 for central
        central_colors[k] = (random.uniform(0.8, 1.0), g, b, 0.8)
        # weak red component < 0.2 for neighbors
        neighbor_colors[k] = (random.uniform(0.0, 0.1), g, b, 0.3)


    # Draw 3x3 blocks
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for k, i, j, o in placements:
                w_cells, h_cells = tile_cells[k][o]
                x0 = i * G + dx * width_cm
                y0 = j * G + dy * height_cm
                w, h = w_cells * G, h_cells * G
                rect = patches.Rectangle((x0, y0), w, h)
                ax.add_patch(rect)
                color = central_colors[k] if (dx, dy) == (0, 0) else neighbor_colors[k]
                rect.set_facecolor(color)
                ax.add_patch(patches.Rectangle((x0, y0), w, h, fill=False, linewidth=1))
                ax.text(x0 + w/2, y0 + h/2, str(k), ha='center', va='center', fontsize=max(G//3, 8))

    ax.set_xlim(-width_cm, 2*width_cm)
    ax.set_ylim(-height_cm, 2*height_cm)
    ax.set_aspect('equal')
    ax.invert_yaxis()
    plt.title(f"Torus Tiling 3x3 of {width_cm}x{height_cm} cm")



    ax.set_xlim(-width_cm, 2*width_cm)
    ax.set_ylim(-height_cm, 2*height_cm)
    ax.set_aspect('equal')
    ax.invert_yaxis()
    plt.title(f"Torus Tiling 3x3 of {width_cm}x{height_cm} cm")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    img = Image.open(buf).copy()
    buf.close()
    plt.close(fig)
    return img


