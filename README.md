# FEChAR

**F**inite **E**lement-based **Ch**arring and **A**blation **R**esponse model

A finite-element solver for the thermal, pyrolysis-gas-transport, and
surface-ablation response of charring ablative thermal protection system
(TPS) materials — the kind of material used on the heat shield of a
spacecraft or hypersonic vehicle. Written in
[FreeFEM++](https://freefem.org/), configured by default with **TACOT** reference material data set so results can be checked against
published benchmarks.

> New to ablation modeling, or to FreeFEM? Start with
> [`docs/THEORY.md`](docs/THEORY.md) for the physics and numerics, then come
> back here to run it.

## What it solves

Given a heating history at the front face, FECHAR marches forward in time
and predicts, through the thickness of the material:

- Temperature
- Local density (i.e. how much of the material has decomposed to char)
- Pyrolysis-gas pressure
- Surface recession (how much material has ablated away)

using two coupled effects: in-depth conduction/decomposition/gas-transport,
and — for convective heating cases — a surface energy balance driven by
pre-tabulated ablation thermochemistry ("B' tables").

## Quick start

### 1. Install FreeFEM++

FECHAR needs [FreeFEM++](https://freefem.org/) (version 4.x). Installers
and instructions for Linux/macOS/Windows are on the
[FreeFEM download page](https://freefem.org/). Once installed, check it
works:

```bash
FreeFem++ -version
```

### 2. Clone and run

```bash
git clone https://github.com/<you>/FE-ChARM.git
cd FE-ChARM
FreeFem++ main.edp
```

That's it — no build step, no dependencies beyond FreeFEM itself. A
progress trace (`t = ...`) prints to the terminal as the simulation
advances, and results are written to a directory named after `casename`
(set in `params.idp`, default `conv2/`).

### 3. Look at the output

Each field is written as tab-separated text, so any plotting tool (Python/
matplotlib, MATLAB, gnuplot, Excel) will read it directly:

| File | Columns | What it is |
|---|---|---|
| `<casename>/out_<t>.dat` | `x`, `T`, `pressure`, `density` | Full through-thickness profile at output time `t` (one file per 0.1 s of simulated time) |
| `<casename>/BCrate.dat` | `t`, `ṡ` (recession rate), `x_wall` | Surface recession history |
| `<casename>/boundarydat.dat` | `t`, `p_wall`, `T_wall`, `B'_g`, `B'_c`, `h_w` | Wall boundary-condition history |
| `<casename>/EnergyBalance.dat` | `t`, then each surface energy-balance term | Term-by-term breakdown of the wall flux balance |
| `<casename>/virgin_loc.dat`, `char_loc.dat` | `t`, threshold density, `x` | Position of the virgin-front / char-front over time |
| `<casename>/massflux.dat` | `t`, pyrolysis gas mass flux, char mass flux | Mass-balance history |
| `<casename>/info.dat` | — | Human-readable run header + summary (what config produced this run) |




## Configuring a run

Everything you're likely to want to change lives in the **USER
CONFIGURATION** block at the top of [`params.idp`](params.idp):

| Setting | Values | Meaning |
|---|---|---|
| `bcType` | `0` | Dirichlet — prescribed surface temperature/pressure history (`Tnew`/`prnew`) |
| | `1` | Convective/B' — aerothermal edge condition (`reuech`/`hblg`) resolved through the B'-table ablation chemistry (default) |
| | `2` | Convective/Q — a net wall heat flux history you already have (`qconvbc`), skipping the B' tables entirely |
| `useRadiation` | `true` / `false` | Surface re-radiation loss (`bcType = 1` or `2`) |
| `useAblation` | `true` / `false` | Surface recession / moving mesh (`bcType = 1` only); when `false`, the surface energy balance still runs but the boundary doesn't move — handy for isolating "heating without recession". `bcType = 2` never recedes, regardless of this flag, since there's no char-blowing parameter (`Bc`) to derive a recession rate from. |
| `casename` | any string | Output subdirectory name |
| `L`, `tend`, `dt`, `ele` | numeric | Domain length [m], simulation end time [s], timestep [s], number of mesh elements |

With `bcType=1, useRadiation=true, useAblation=true` the solver reproduces
the original TACOT convective-ablation benchmark. **Run that combination
first** and compare against a known-good result before trusting other
configurations, the same way you'd check any new solver install.

To change the *time history* of wall temperature/pressure/heating (as
opposed to which physics is active), edit or add a macro in
[`Datafolder/bc/Boundary1.idp`](Datafolder/bc/Boundary1.idp) and point the
relevant name (`Tnew`, `reuech`, `hblg`, `qconvbc`, ...) at it — these are
plain piecewise-linear ramp functions of time, easy to copy and modify for
a new heating pulse shape.

### Already have a heat flux instead of a boundary-layer edge condition?

`bcType = 1` expects an edge mass flux (`reuech`) and recovery enthalpy
(`hblg`), which get run through the B'-table ablation chemistry to find
the wall energy balance. If you already have the net wall heat flux
history `q(t)` from somewhere else (a separate aerothermal/CFD run, test
data, ...), set `bcType = 2` instead and define `qconvbc(t)` in
`Datafolder/bc/Boundary1.idp` — the solver uses it directly and skips the
B'-table lookup. The trade-off: with no char-blowing parameter (`Bc`)
computed, `bcType = 2` has no surface recession, so use it for
heating-response-only cases.

## How it's organized

```
main.edp           entry point — run this. Variational forms + time loop.
params.idp         USER CONFIGURATION, physical constants, material/BC tables
meshsetup.idp       1D mesh, finite-element space, fields, initial conditions
Datafolder/
  Macro_operator.idp    generic FreeFEM helper macros (gradient/divergence/...)
  bc/Boundary1.idp        time-history macros for the wall BC (edit here for a new case)
  tacotdata/               TACOT material property correlations + the B' ablation tables
docs/
  THEORY.md              governing equations and numerical method, explained
legacy/               earlier drafts / table-generation scratch work (not used by the solver — see legacy/README.md)
```

`main.edp` includes the other files in a fixed order — `params.idp` →
mesh/BC/operator macros → `meshsetup.idp` → `output.idp` — because each
later file depends on constants or fields declared by an earlier one; see
the comment block at the top of `main.edp` for the exact dependency chain.

## Generalizing beyond TACOT

`Datafolder/tacotdata/macro2.idp` currently hard-codes TACOT's property
correlations (`cpv`, `kv`, `hv`, `cpc`, `kc`, `hc`, decomposition kinetics
`denvarA/B/C`) and its B' ablation tables. Swapping in a different
material's data means replacing that file (and its underlying `.dat`/`.txt`
tables) — `main.edp`'s solver logic doesn't need to change, since it only
calls the macro *names*, not the correlations themselves.

If you want a second material to coexist in the repo rather than replace
TACOT, the natural next step is moving `Datafolder/tacotdata/` to something
like `materials/tacot/` and `materials/<newmaterial>/`, and pointing
`params.idp`'s `include`/`ifstream` paths at whichever is active. That's a
bigger data-schema decision than a quick edit, so it's left as a follow-up
rather than done preemptively here — see
[`CONTRIBUTING.md`](CONTRIBUTING.md) if you want to take this on.

## Validating a change

There's no automated test suite (FreeFEM doesn't lend itself to one
easily), so the practical regression check is: run the default TACOT
benchmark configuration (`bcType=1, useRadiation=true, useAblation=true`)
before and after your change, and confirm the wall temperature history in
`boundarydat.dat` and the recession history in `BC.dat` haven't moved
outside numerical noise. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for more.

## Citing / provenance

FECHAR implements a standard 1D charring-ablator response model (in-depth
conduction + pyrolysis decomposition + Darcy gas transport + B'-method
surface ablation) evaluated against NASA's TACOT reference material — see
[`docs/THEORY.md`](docs/THEORY.md) for the equations and the papers this
follows.

## Publishing this repo

```bash
git init
git add .
git commit -m "Initial commit: FECHAR 1D ablation response solver"
git branch -M main
git remote add origin https://github.com/<you>/FECHAR.git
git push -u origin main
```

`.gitignore` already excludes generated output directories and editor/OS
cruft — the input `.dat`/`.txt` material and ablation-table data under
`Datafolder/` is tracked on purpose (it's input data the solver needs, not
generated output).

## License

See [`LICENSE`](LICENSE).
