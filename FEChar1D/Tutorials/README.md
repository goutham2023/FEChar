# Tutorials

Three ready-to-run cases. Each folder is self-contained: **open a terminal inside the folder and run FreeFEM from there**, because the data paths are relative (`../../Datafolder/...`).

| Folder | What is prescribed at the heated face | Needs B' tables | Surface recession |
|---|---|---|---|
| `DirichletBC` | wall temperature ramp (to 1644 K) | no | no |
| `ConvectiveQcase` | net wall heat-flux ramp (to 500 kW/m²) | no | no |
| `ConvectiveRamp_Bprime` | aerothermal edge condition ramp (`ρeueCH`, recovery enthalpy) | **yes**, for the chosen environment | **yes** |

Start with **`ConvectiveRamp_Bprime`**. Its folder contains

- `Tutorial_ConvectiveRamp_Bprime.pdf`: step-by-step guide to the ramp problem in any environment (Earth, Mars, Venus, Titan), including how to change the ramp and how to read the results;
- `run_all_environments.sh`: runs all four environments in turn;
- `reference_results/`: outputs of a quick run, to check that an installation works.

## How to run

```bash
cd Tutorials/ConvectiveRamp_Bprime
FreeFem++ -nw main.edp                                  # settings from params.idp
FreeFem++ -nw main.edp -env Mars -heat low -tend 10     # command-line overrides
```

Flags: `-env -heat -tend -ele -dt -tup -toff -tdown`, see the main [README](../README.md#command-line-overrides).

## How the folders differ

`main.edp`, `meshsetup.idp` and `fespace_init_varf.idp` are identical in the three folders. `params.idp` differs only in two lines: `bcType` (0, 1 or 2) and `useAblation`. The solver reads everything else from `../../Datafolder`.

To start your own case, copy one folder, rename it, and edit its `params.idp`.

## Notes

- Each run deletes and recreates its output folder `case_...` (see `.gitignore`).
- Use `dt <= 0.005 s`. Larger steps made the iteration diverge in tests, and the Dirichlet case is the most sensitive. For quick tests reduce `-tend` and `-ele` (250 is enough to see the behaviour) instead.
