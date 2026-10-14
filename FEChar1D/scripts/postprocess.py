
#!/usr/bin/env python3
"""Quick-look figures for FEChAR case folders.

Usage:
    python scripts/plot_results.py case_Earth_Bprime_high
    python scripts/plot_results.py case_Earth_Bprime_high case_Mars_Bprime_high --outdir figures

Existing figures:
    wall_temperature.png
    recession.png
    blowing.png
    profiles.png

Additional figures (if the corresponding data files exist):
    interfaces.png
    probe_temperature.png
    probe_pressure.png
    probe_density.png
"""

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


import re

RHO_VIRGIN_98 = 278.8
RHO_CHAR_02 = 221.2
DEFAULT_DEPTHS = [0.001, 0.002, 0.004, 0.008, 0.012, 0.016, 0.024]


def load_numeric_file(path):
    """Load numeric columns, ignoring blank and comment/header lines."""
    return np.atleast_2d(np.loadtxt(path, comments="#"))


def load_profile(path):
    """Read a profile file; expected columns are x, temperature, pressure, density."""
    arr = load_numeric_file(path)
    if arr.shape[1] < 4:
        raise ValueError(f"{path}: expected at least 4 columns (x, T, p, rho)")
    return arr


def load_table(case, filename):
    path = os.path.join(case, filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Required data file not found: {path}")
    return load_numeric_file(path)


def profile_files(case):
    """Return (time, path) pairs from files named out_<time>.dat, sorted by time."""
    found = []
    pattern = re.compile(r"^out_([-+0-9.eE]+)\.dat$")
    if not os.path.isdir(case):
        raise FileNotFoundError(f"Case folder not found: {case}")
    for name in os.listdir(case):
        match = pattern.match(name)
        if match:
            try:
                found.append((float(match.group(1)), os.path.join(case, name)))
            except ValueError:
                pass
    return sorted(found, key=lambda item: item[0])


def first_crossing(x, rho, level):
    """Linearly interpolate the first density crossing; return 0 if absent."""
    for i in range(len(x) - 1):
        r0, r1 = rho[i], rho[i + 1]
        if (r0 - level) * (r1 - level) <= 0 and r0 != r1:
            return x[i] + (level - r0) * (x[i + 1] - x[i]) / (r1 - r0)
    return 0.0


def generate_probe_files(case, depths=DEFAULT_DEPTHS):
    rows = {"temperature": [], "pressure": [], "density": []}
    files = profile_files(case)
    for t, path in files:
        d = load_profile(path)
        x = d[:, 0]
        for key, col in (("temperature", 1), ("pressure", 2), ("density", 3)):
            vals = [
                np.interp(z, x, d[:, col]) if x[0] <= z <= x[-1] else 0.0
                for z in depths
            ]
            rows[key].append([t] + vals)

    header = "time[s] " + " ".join(f"x={z:g}m" for z in depths)
    for key, values in rows.items():
        target = os.path.join(case, f"probes_{key}.dat")
        np.savetxt(target, np.asarray(values).reshape((-1, len(depths) + 1)),
                   fmt="%.6g", header=header)
        print("wrote", target)


def generate_interface_file(case):
    rows = []
    for t, path in profile_files(case):
        d = load_profile(path)
        rows.append([t, first_crossing(d[:, 0], d[:, 3], RHO_VIRGIN_98),
                     first_crossing(d[:, 0], d[:, 3], RHO_CHAR_02)])
    target = os.path.join(case, "interfaceloc.dat")
    np.savetxt(target, np.asarray(rows).reshape((-1, 3)), fmt="%.6g",
               header="time[s] x_virgin_front[m] x_char_front[m]")
    print("wrote", target)



def label_of(case):
    name = os.path.basename(os.path.normpath(case))
    return name[5:] if name.startswith("case_") else name


def load_probe_file(path):
    """Load probe data and extract depth labels from its header."""
    with open(path, "r") as f:
        header = f.readline().strip().lstrip("#").strip()

    columns = header.split()
    depths = columns[1:] if len(columns) > 1 else []

    data = load_numeric_file(path)
    return data, depths


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("cases", nargs="+", help="one or more case folders")
    ap.add_argument("--outdir", default="figures",
                    help="output folder for PNG files")
    ap.add_argument("--xmax", type=float, default=None,
                    help="upper limit of the time axis [s]")
    ap.add_argument("--times", type=float, nargs="+", default=None,
                    help="times [s] for profiles.png")
    ap.add_argument("--depth-mm", type=float, default=50.0,
                    help="depth range of profiles.png [mm]")
    ap.add_argument("--depths", type=float, nargs="+", default=DEFAULT_DEPTHS,
                    help="probe depths in metres (default: %(default)s)")
    args = ap.parse_args()

    # Pre-processing: generate probe histories and interface locations before plotting.
    for case in args.cases:
        if not os.path.isdir(case):
            ap.error(f"case folder does not exist: {case}")
        profiles = profile_files(case)
        if not profiles:
            print(f"WARNING: no out_<time>.dat profile files found in {case}")
        generate_probe_files(case, args.depths)
        generate_interface_file(case)

    os.makedirs(args.outdir, exist_ok=True)

    data = {}
    for c in args.cases:
        bd = load_table(c, "boundarydat.dat")
        bc = load_table(c, "BC.dat")
        data[c] = (bd, bc)

    def finish(ax, ylabel, fname):
        ax.set_xlabel("Time [s]")
        ax.set_ylabel(ylabel)

        if args.xmax is not None:
            ax.set_xlim(0, args.xmax)

        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
        ax.figure.tight_layout()

        path = os.path.join(args.outdir, fname)
        ax.figure.savefig(path, dpi=200)
        plt.close(ax.figure)
        print("wrote", path)

    def lw(i):
        return max(1.2, 2.8 - 0.5 * i)

    # ---------------------------------------------------------
    # 1. Wall temperature
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 4))
    for i, (c, (bd, bc)) in enumerate(data.items()):
        ax.plot(bd[:, 0], bd[:, 2], lw=lw(i), label=label_of(c))

    finish(ax, "Wall temperature [K]", "wall_temperature.png")

    # ---------------------------------------------------------
    # 2. Surface recession
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 4))
    for i, (c, (bd, bc)) in enumerate(data.items()):
        recession = 1e3 * (bc[:, 2] - bc[0, 2])
        ax.plot(bc[:, 0], recession, lw=lw(i), label=label_of(c))

    finish(ax, "Surface recession [mm]", "recession.png")

    # ---------------------------------------------------------
    # 3. Blowing parameters
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 4))
    for i, (c, (bd, bc)) in enumerate(data.items()):
        col = f"C{i}"
        ax.plot(bd[:, 0], bd[:, 4], color=col,
                label=f"B'c - {label_of(c)}")
        ax.plot(bd[:, 0], bd[:, 3], color=col, ls="--",
                label=f"B'g - {label_of(c)}")

    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Blowing parameter [-]")
    if args.xmax is not None:
        ax.set_xlim(0, args.xmax)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    fig.tight_layout()

    path = os.path.join(args.outdir, "blowing.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print("wrote", path)

    # ---------------------------------------------------------
    # 4. In-depth temperature profiles (first case)
    # ---------------------------------------------------------
    first = args.cases[0]
    files = profile_files(first)

    if files:
        tmax = files[-1][0]
        targets = args.times or [
            f * tmax for f in (0.05, 0.25, 0.5, 0.75, 1.0)
        ]

        fig, ax = plt.subplots(figsize=(6, 4))

        for tt in targets:
            t, path = min(files, key=lambda f: abs(f[0] - tt))
            d = load_profile(path)
            ax.plot(1e3 * d[:, 0], d[:, 1], label=f"t = {t:g} s")

        ax.set_xlabel("x from original surface [mm]")
        ax.set_ylabel("Temperature [K]")
        ax.set_xlim(0, args.depth_mm)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
        fig.tight_layout()

        path = os.path.join(args.outdir, "profiles.png")
        fig.savefig(path, dpi=200)
        plt.close(fig)
        print("wrote", path)

    # ---------------------------------------------------------
    # 5. Interface positions from interfaceloc.dat
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 4))
    found = False

    for i, c in enumerate(args.cases):
        path = os.path.join(c, "interfaceloc.dat")

        if not os.path.isfile(path):
            print("skipping missing file:", path)
            continue

        arr = load_numeric_file(path)
        if arr.shape[1] < 3:
            print("skipping invalid interface file:", path)
            continue

        ax.plot(arr[:, 0], arr[:, 1] * 1e3,
                color=f"C{i}", ls="-",
                label=f"Virgin front - {label_of(c)}")
        ax.plot(arr[:, 0], arr[:, 2] * 1e3,
                color=f"C{i}", ls="--",
                label=f"Char front - {label_of(c)}")
        found = True

    if found:
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Interface position from original surface [mm]")
        if args.xmax is not None:
            ax.set_xlim(0, args.xmax)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
        fig.tight_layout()

        path = os.path.join(args.outdir, "interfaces.png")
        fig.savefig(path, dpi=200)
        print("wrote", path)
    else:
        print("No interface data found; interfaces.png not generated.")

    plt.close(fig)

    # ---------------------------------------------------------
    # 6. Probe temperature, pressure and density histories
    # ---------------------------------------------------------
    probe_types = {
        "temperature": ("Temperature [K]", "probe_temperature.png"),
        "pressure": ("Pressure [Pa]", "probe_pressure.png"),
        "density": (r"Density [kg/m$^3$]", "probe_density.png"),
    }

    for quantity, (ylabel, filename) in probe_types.items():
        fig, ax = plt.subplots(figsize=(8, 5))
        found = False

        for i, c in enumerate(args.cases):
            path = os.path.join(c, f"probes_{quantity}.dat")

            if not os.path.isfile(path):
                print("skipping missing file:", path)
                continue

            arr, depths = load_probe_file(path)

            if arr.shape[1] < 2:
                print("skipping probe file with no probe columns:", path)
                continue

            for j in range(1, arr.shape[1]):
                if j - 1 < len(depths):
                    probe_label = depths[j - 1]
                else:
                    probe_label = f"probe {j}"

                ax.plot(
                    arr[:, 0], arr[:, j],
                    lw=1.5,
                    label=f"{label_of(c)}: {probe_label}"
                )
                found = True

        if found:
            ax.set_xlabel("Time [s]")
            ax.set_ylabel(ylabel)
            if args.xmax is not None:
                ax.set_xlim(0, args.xmax)
            ax.grid(alpha=0.3)
            ax.legend(fontsize=7, ncol=2)
            fig.tight_layout()

            path = os.path.join(args.outdir, filename)
            fig.savefig(path, dpi=200)
            print("wrote", path)
        else:
            print(f"No {quantity} probe data found; {filename} not generated.")

        plt.close(fig)


if __name__ == "__main__":
    main()