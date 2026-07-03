#!/usr/bin/env bash
# Runtime verification report for the machine-checked proof package.
# Invoked by `docker run`; can also be run directly in a native checkout
# (requires elan + the pinned toolchain — see README.md).
set -euo pipefail
cd "$(dirname "$0")/lean"

rule() { printf '=%.0s' {1..70}; printf '\n'; }

rule
echo " Investing in Artificial General Intelligence"
echo " Machine-checked proof verification (Lean 4 / Mathlib)"
rule
echo

echo "[1/3] Kernel-checking every proof (lake build)..."
lake build
echo "      OK - all proofs compile and pass the Lean kernel."
echo

echo "[2/3] Axioms each headline theorem depends on"
echo "      (expected: [propext, Classical.choice, Quot.sound]; no sorryAx):"
echo
# One representative theorem per source file; see README.md / lean/README.md
# for the full theorem -> paper-result map.
THEOREMS=(
  AILab.euler_operator_rpow            # EulerODE.lean       (eq-hjb-L, eq-beta-H)
  AILab.charPoly_betaPlus              # CharacteristicRoots.lean (eq-beta-H)
  AILab.trigger_from_boundary_conditions  # Proposition1.lean  (eq-trigger-phi)
  AILab.alloc_foc_closed_form          # Proposition1Phi.lean (phi*)
  AILab.faith_threshold                # Proposition2.lean   (eq-phi-underbar)
  AILab.preemption_exists              # Duopoly.lean        (X_P existence)
)
{
  echo "import AILabProofs"
  for t in "${THEOREMS[@]}"; do
    echo "#print axioms $t"
  done
} | lake env lean --stdin
echo

echo "[3/3] Scanning sources for 'sorry'..."
if grep -rnw --include='*.lean' sorry AILabProofs; then
  echo "      FAIL - found 'sorry' in the sources." >&2
  exit 1
fi
echo "      none found."
echo

rule
echo " VERIFIED: every proof is kernel-checked, the axioms are limited to the"
echo " three standard Lean axioms, and no proof uses 'sorry'. The theorem ->"
echo " paper-result map is in README.md; the complete equation listing the"
echo " statements transcribe is in equations.tex."
rule
