"""Shared helpers for the FEChAR post-processing scripts (NumPy only)."""
import glob
import os
import re

import numpy as np


def profile_files(case):
    """Return [(time, path), ...] for all out_<t>.dat files of a case folder, sorted by time."""
    files = []
    for path in glob.glob(os.path.join(case, "out_*.dat")):
        m = re.match(r"out_(.+)\.dat$", os.path.basename(path))
        if m:
            files.append((float(m.group(1)), path))
    if not files:
        raise SystemExit(f"No out_<t>.dat files found in '{case}'. Run the solver first, "
                         f"and pass the case folder (e.g. case_Earth_Bprime_high).")
    return sorted(files)


def load_profile(path):
    """Columns: x [m], T [K], pressure [Pa], density [kg/m3]."""
    return np.loadtxt(path)


def load_table(case, name):
    """Load a tab-separated output file such as boundarydat.dat; returns a 2-D array."""
    path = os.path.join(case, name)
    if not os.path.isfile(path):
        raise SystemExit(f"File not found: {path}")
    return np.atleast_2d(np.loadtxt(path))
