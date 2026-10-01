# FEChAR

**F**inite **E**lement-based **Ch**arring and **A**blation **R**esponse model

A [FreeFEM++](https://freefem.org/) solver for the thermal, pyrolysis-gas transport, and surface-ablation response of charring ablative heat-shield materials. It ships with the **TACOT** reference material, so results can be checked against published benchmarks.

For the governing equations and numerical method, see [`docs/THEORY.md`](docs/THEORY.md).

## What it solves

Given a heating history at the front face, FEChAR marches in time and predicts through the material thickness:

- temperature
- density (degree of decomposition to char)
- pyrolysis-gas pressure
- surface recession

It couples in-depth conduction, pyrolysis, and Darcy gas flow with a surface energy balance driven by pre-tabulated ablation chemistry (B' tables).


# FEChAR1D

1D model uses B' formulation for material recession prediction
## Quick start

Install [FreeFEM++](https://freefem.org/) (4.x), then:

```bash
git clone https://github.com/<your-username>/FEChAR.git
cd FEChAR
FreeFem++ main.edp
```

No build step or other dependencies. Progress prints to the terminal, and results go to a folder named after `casename` (set in `params.idp`, default `conv2/`).

## Configuration

Edit the **USER CONFIGURATION** block at the top of [`params.idp`](params.idp):

| Setting | Values | Meaning |
|---|---|---|
| `bcType` | `0` | Prescribed wall temperature and pressure (`Tnew`, `prnew`) |
| | `1` | Aerothermal edge condition (`reuech`, `hblg`) resolved through the B' tables (default) |
| | `2` | Net wall heat flux history (`qconvbc`); skips the B' tables and has no recession |
| `useRadiation` | `true` / `false` | Surface re-radiation (`bcType` 1 or 2) |
| `useAblation` | `true` / `false` | Surface recession and moving mesh (`bcType = 1` only) |
| `casename` | string | Output folder name |
| `L`, `tend`, `dt`, `ele` | numbers | Thickness [m], end time [s], time step [s], number of elements |

To change the heating history, edit or add a macro in [`Datafolder/bc/Boundary1.idp`](Datafolder/bc/Boundary1.idp). The wall functions (`Tnew`, `reuech`, `hblg`, `qconvbc`) are simple piecewise-linear functions of time.

**Sanity check:** run `bcType=1, useRadiation=true, useAblation=true` first. This reproduces the TACOT convective-ablation benchmark.

## Output

All files are tab-separated text and can be read by any plotting tool.

| File (in `<casename>/`) | Contents |
|---|---|
| `out_<t>.dat` | `x`, `T`, pressure, density profile (one file per 0.1 s) |
| `BCrate.dat` | `t`, recession rate, wall position |
| `boundarydat.dat` | `t`, `p_wall`, `T_wall`, `B'_g`, `B'_c`, `h_w` |
| `EnergyBalance.dat` | `t` and each surface energy-balance term |
| `virgin_loc.dat`, `char_loc.dat` | virgin and char front positions vs time |
| `massflux.dat` | `t`, pyrolysis-gas and char mass flux |
| `info.dat` | run header and configuration summary |

## Repository layout

```
main.edp          entry point: variational forms and time loop
params.idp        user configuration, constants, material/BC tables
meshsetup.idp     1D mesh, finite-element space, initial conditions
Datafolder/
  Macro_operator.idp   generic FreeFEM helper macros
  bc/Boundary1.idp     wall boundary-condition histories
  tacotdata/           TACOT property correlations and B' tables
docs/THEORY.md    governing equations and numerics
legacy/           earlier drafts, not used by the solver
```

`main.edp` includes files in a fixed order (`params.idp`, mesh/BC/operator macros, `meshsetup.idp`, `output.idp`), because each depends on the one before it. See the comment at the top of `main.edp`.

## Using a different material

The solver only calls macro names such as `cpv`, `kv`, `hv`, `cpc`, `kc`, `hc`, and `denvarA/B/C`. To change material, replace `Datafolder/tacotdata/macro2.idp` and its `.dat`/`.txt` tables; `main.edp` stays the same.

## Validating changes

There is no automated test suite. Run the default benchmark before and after a change and confirm that `T_wall` in `boundarydat.dat` and the recession history in `BCrate.dat` are unchanged within numerical noise. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

See [`LICENSE`](LICENSE).

# FEChAR1D-M++

