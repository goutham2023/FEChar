#!/usr/bin/env bash
# Run the ramp problem for every environment (Earth, Mars, Venus, Titan).
#
# Usage (from anywhere):
#   ./run_all_environments.sh                         # production settings from params.idp
#   ./run_all_environments.sh -tend 10 -ele 100 -dt 0.02   # quick test of all four
#   HEAT=low ./run_all_environments.sh                # another heating level
#   FREEFEM=/path/to/FreeFem++ ./run_all_environments.sh   # non-default FreeFEM binary
#
# Each run writes its own folder: case_<Environment>_Bprime_<heat>/
set -e
cd "$(dirname "$0")"
FREEFEM=${FREEFEM:-FreeFem++}
HEAT=${HEAT:-high}
for env in Earth Mars Venus Titan; do
    echo "=== ${env}, heating level: ${HEAT} ==="
    "$FREEFEM" -nw main.edp -env "$env" -heat "$HEAT" "$@"
done
echo "Done. Result folders: $(ls -d case_*_Bprime_${HEAT} | tr '\n' ' ')"
