# Machine-checked proof package — *Investing in Artificial General Intelligence*

This package lets a referee verify the paper's closed-form results without
checking the algebra by hand. It contains a formalization of the paper's
derivations in [Lean 4](https://lean-lang.org/) against
[Mathlib](https://github.com/leanprover-community/mathlib4), the community
mathematics library. Every theorem is checked by the Lean kernel: there are no
unproven placeholders (`sorry`-free), and every result depends only on Lean's
three standard axioms (`propext`, `Classical.choice`, `Quot.sound`). If the
package builds, the proofs are correct — the only question left for a human
(or AI) reader is whether the formal statements faithfully transcribe the
paper's equations, which is what `equations.tex` is for (see below).

## Contents

| Path | What it is |
|:-----|:-----------|
| `lean/` | The Lean 4 project (`AILabProofs`). Seven source files under `lean/AILabProofs/`, one per cluster of results. |
| `lean/README.md` | The complete theorem-by-theorem map from Lean names to paper propositions and equation labels, plus the precise scope (what is and is not formalized). |
| `equations.tex` | Every display equation of the paper and the Internet Appendix, in source order, each with its introducing prose and its equation label (e.g. `eq-trigger-phi`). Auto-generated from the manuscript source, so it cannot drift from the paper. |

## What is verified

The algebraic and single-variable-calculus content of Propositions 1–3 — the
steps a referee would otherwise check by hand:

- the reduction of the homogeneous Euler ODE to the characteristic equation,
  and the characteristic roots with their ordering (`EulerODE.lean`,
  `CharacteristicRoots.lean`);
- the investment trigger, NPV at the trigger, and capacity and allocation
  first-order conditions with their closed forms, including uniqueness of the
  interior training fraction (`Proposition1.lean`, `Proposition1Phi.lean`);
- the faith-based-survival threshold and the default-boundary comparative
  statics (`Proposition2.lean`);
- the duopoly role-invariance of the allocation, the follower's separable
  reduction, and the existence and (zero-leverage) uniqueness of the
  preemption trigger (`Duopoly.lean`).

Results are stated for abstract parameters under the paper's admissibility
assumptions, so each theorem holds for *every* admissible parameter value,
not just the baseline calibration.

**Not formalized** (see `lean/README.md` for the precise list): the derivation
of the HJB equation from stochastic-calculus primitives and the
optimal-stopping verification theorem (taken as the starting point, as in the
paper's appendix), and all numerical results. Numerical results are
reproducible from the public code repository:
<https://github.com/fintech-research/ai-lab-investment/>.

## How to read it (no Lean experience needed)

1. Start with the table in `lean/README.md`, which maps each theorem to the
   paper result it verifies.
2. Open the corresponding file in `lean/AILabProofs/`. Each file begins with a
   docstring cross-referencing the paper's equation labels. A theorem
   statement reads like the paper: everything before the final `:` lists the
   hypotheses (parameter-sign and admissibility assumptions), and what follows
   is the verified identity or inequality. The proof below it can be ignored —
   the kernel has checked it.
3. Cross-check statements against `equations.tex`, which contains the paper's
   equations under the same labels.

### Checking faithfulness with an AI agent

The one thing the Lean kernel cannot certify is that the formal statements
match the paper. `equations.tex` exists so that this check can be delegated to
an AI coding agent (e.g. Claude Code or Codex) instead of done by hand. The
manuscript is public (SSRN and the GitHub repository above), so no
confidentiality concern arises from uploading this package to such tools.
A suggested prompt:

> `equations.tex` contains every display equation of a finance paper, tagged
> with labels like `eq-trigger-phi`. `lean/AILabProofs/` contains Lean 4
> theorems whose docstrings reference those labels, and `lean/README.md` maps
> theorems to paper results. For each theorem: (1) find the corresponding
> equation(s) in `equations.tex`; (2) check that the Lean statement — its
> hypotheses and its conclusion — is a faithful transcription, flagging any
> mismatch in functional form, sign conventions, parameter restrictions, or
> strictness of inequalities; (3) flag any theorem that proves something
> weaker than the paper claims. Report a table: theorem, paper label(s),
> verdict, and any discrepancies.

## How to execute it

Requires [`elan`](https://github.com/leanprover/elan), the Lean toolchain
manager (the toolchain version is pinned in `lean/lean-toolchain`):

```bash
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh
```

Then build (first run downloads prebuilt Mathlib binaries, ~2–3 GB; the build
itself takes a few minutes):

```bash
cd lean
lake exe cache get   # download prebuilt Mathlib oleans (first time only)
lake build           # kernel-checks every proof; exits 0 iff all proofs pass
```

To confirm a theorem is `sorry`-free and uses only standard axioms:

```bash
printf 'import AILabProofs\n#print axioms AILab.alloc_foc_closed_form\n' | lake env lean --stdin
# 'AILab.alloc_foc_closed_form' depends on axioms: [propext, Classical.choice, Quot.sound]
```

---

*Package maintainers: `equations.tex` is generated by `extract_equations.py`
from the paper's Quarto sources — regenerate it (`just
build-replication-package` from the repository root) rather than editing it.*
