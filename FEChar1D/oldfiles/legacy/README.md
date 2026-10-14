# legacy/

Earlier drafts and scratch work kept for provenance. **Nothing in this
folder is included by `main.edp`** — the active solver never reads these
files. They're here so the history of how the TACOT tables were built isn't
lost, not because you need them to run FECHAR.

| File | What it is |
|---|---|
| `macro2new.idp` | An earlier version of `Datafolder/tacotdata/macro2.idp`, with a different set of boundary-condition macros (`Tnew2`, `Tnew3`, `reuech2`, ...) mixed in. Superseded by `macro2.idp` + `Datafolder/bc/Boundary1.idp`. |
| `gasgrid.idp` | A loader for a 2D (pressure, temperature) pyrolysis-gas property grid. References a stream (`ISTP2`) that's never opened anywhere in this repo — it was written to be pasted after a manual `ifstream` declaration, not `include`d directly. Superseded by the 1D-in-temperature lookup (`TE3`/`Hpref`/... in `params.idp`, read from `pyrogas_prop.txt`). |
| `trial.ipynb` | A Python notebook that reads `pressure_pyrogas.dat` and reshapes it into the (P, T) grid format `gasgrid.idp` expects — i.e. the preprocessing step that would sit upstream of `gasgrid.idp`. |
| `pressure_pyrogas.dat`, `gasdata.dat`, `grid_data.dat`, `Qconv.txt`, `Qconv2.txt`, `Tw_unique.txt` | Raw/intermediate data tables associated with the (P, T) grid approach above. |

If you want to resurrect the (P, T)-grid gas-property approach (instead of
the current 1D-in-temperature lookup), this is your starting point — but
expect to have to finish wiring it up (open `ISTP2` yourself, decide where
`Mugrid`/`cpgrid`/`gammagrid`/`Hgrid` get used in `main.edp`, etc.).
