from functools import reduce
from math import gcd

from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import os
import re

# Tile formats in centimeters
FORMATS = {
    1: (20, 20),
    2: (20, 40),
    3: (40, 40),
    4: (40, 60),
    5: (60, 60),
    6: (60, 90),
}
# Weights for each tile type
WEIGHTS = {
    1: 2,
    2: 3,
    3: 5,
    4: 8,
    5: 11,
    6: 30,
}

PENALTY_WEIGHT = 50

def solve_torus_tiling(width_cm, height_cm, G):
    assert width_cm % G == 0 and height_cm % G == 0, \
        f"Floor dimensions must be multiples of {G}cm"
    W, H = width_cm // G, height_cm // G
    model = cp_model.CpModel()

    # Precompute tile sizes in grid cells
    tile_cells = {k: [(w // G, h // G), (h // G, w // G)] for k, (w, h) in FORMATS.items()}

    # Placement variables
    X = {}
    for k in FORMATS:
        for o, (w_c, h_c) in enumerate(tile_cells[k]):
            for i in range(W):
                for j in range(H):
                    X[k, i, j, o] = model.NewBoolVar(f"X_{k}_{i}_{j}_{o}")

    # Coverage constraint
    for x in range(W):
        for y in range(H):
            model.Add(
                sum(
                    X[k, i, j, o]
                    for k in FORMATS
                    for o, (w_c, h_c) in enumerate(tile_cells[k])
                    for i in range(W)
                    for j in range(H)
                    if ((x - i) % W) < w_c and ((y - j) % H) < h_c
                ) == 1
            )

    # Each tile type >=1
    # for k in FORMATS:
    #     model.Add(sum(X[k, i, j, o] for i in range(W) for j in range(H) for o in [0,1]) >= 1)
    model.Add(sum(X[6, i, j, o] for i in range(W) for j in range(H) for o in [0, 1]) >= 1)
    # Non-trivial wrap
    model.Add(
        sum(X[k,i,j,o] for k in FORMATS for o,(w_c,h_c) in enumerate(tile_cells[k]) for i in range(W) for j in range(H) if j + h_c > H) >= 1
    )
    model.Add(
        sum(X[k,i,j,o] for k in FORMATS for o,(w_c,h_c) in enumerate(tile_cells[k]) for i in range(W) for j in range(H) if i + w_c > W) >= 1
    )

    # No full straight lines
    for b in range(W):
        model.Add(
            sum(X[k,i,j,o] for k in FORMATS for o,(w_c,_) in enumerate(tile_cells[k]) for i in range(W) for j in range(H) if 0 < ((b - i) % W) < w_c) >= 1
        )
    for r in range(H):
        model.Add(
            sum(X[k,i,j,o] for k in FORMATS for o,(_,h_c) in enumerate(tile_cells[k]) for i in range(W) for j in range(H) if 0 < ((r - j) % H) < h_c) >= 1
        )

    # Four-corner penalty variables
    C = {}
    for b in range(W):
        for r in range(H):
            C[b,r] = model.NewBoolVar(f"C_{b}_{r}")
            # sum of corners at (b,r)
            corner_sum = []
            for k in FORMATS:
                for o,(w_c,h_c) in enumerate(tile_cells[k]):
                    for i in range(W):
                        for j in range(H):
                            # corner positions
                            if ((i % W) == b and (j % H) == r) or \
                               ((i + w_c) % W == b and (j % H) == r) or \
                               ((i % W) == b and (j + h_c) % H == r) or \
                               ((i + w_c) % W == b and (j + h_c) % H == r):
                                corner_sum.append(X[k,i,j,o])
            # Exactly four corners -> C[b,r]=1
            model.Add(sum(corner_sum) == 4).OnlyEnforceIf(C[b,r])
            model.Add(sum(corner_sum) <= 3).OnlyEnforceIf(C[b,r].Not())

    # Objective: weighted tiles + penalty for four-corner points
    model.Minimize(
        sum(WEIGHTS[k] * X[k,i,j,o] for k in FORMATS for i in range(W) for j in range(H) for o in [0,1])
        + PENALTY_WEIGHT * sum(C.values())
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("No solution found.")
        return None

    placements = [(k,i,j,o) for (k,i,j,o), var in X.items() if solver.Value(var)]
    return placements, W*G, H*G, G


def draw_tiling(placements, width_cm, height_cm, G):
    # Recompute tile_cells for drawing
    tile_cells = {
        k: [(w // G, h // G), (h // G, w // G)]
        for k, (w, h) in FORMATS.items()
    }

    fig, ax = plt.subplots()
    # Colors for central block and neighbors
    # Colors for central block (strong red) and neighbors (weak red)
    central_colors = {}
    neighbor_colors = {}
    for k in FORMATS:
        g = random.random()
        b = random.random()
        # strong red component > 0.5 for central
        central_colors[k] = (random.uniform(0.8, 1.0), g, b, 0.8)
        # weak red component < 0.2 for neighbors
        neighbor_colors[k] = (random.uniform(0.0, 0.1), g, b, 0.3)

    # Determine next available filename
    existing = [f for f in os.listdir('.') if re.match(r'uklad-\d+\.png$', f)]
    nums = [int(re.search(r'uklad-(\d+)\.png', f).group(1)) for f in existing]
    next_num = max(nums) + 1 if nums else 1
    filename = f"uklad-{next_num}.png"

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
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Saved tiling figure to {filename}")
    #plt.show()


if __name__ == '__main__':
    # Iterate floor dimensions from 100 to 300 cm in steps of 10
    all_dims = [dim for wh in FORMATS.values() for dim in wh]
    G = reduce(gcd, all_dims)
    for H_cm in range(100, 361, G):
        for W_cm in range(H_cm, 361, G):
            print(f"Solving torus tiling for {W_cm}x{H_cm} cm...")
            result = solve_torus_tiling(W_cm, H_cm, G)
            if result:
                placements, w_cm, h_cm, G_out = result
                # Compute total weighted count
                total_weight = sum(WEIGHTS[k] for k, _, _, _ in placements)
                print(f"  -> Found solution: {len(placements)} tiles, total weight {total_weight}")
                draw_tiling(placements, w_cm, h_cm, G_out)
            else:
                print(f"  -> No solution for {W_cm}x{H_cm} cm.")
