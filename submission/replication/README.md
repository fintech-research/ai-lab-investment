# Machine-checked proof package — *Investing in Artificial General Intelligence*

This package lets a referee check closed-form steps of the paper without redoing the algebra by hand. It contains a formalization of parts of the paper's derivations in [Lean 4](https://lean-lang.org/) against [Mathlib](https://github.com/leanprover-community/mathlib4), the community mathematics library. Every theorem is checked by the Lean kernel: there are no unproven placeholders (`sorry`-free), and every result depends only on Lean's three standard axioms (`propext`, `Classical.choice`, `Quot.sound`). If the package builds, the formal proofs have no gaps. Two questions remain for a human (or AI) reader: whether the formal statements faithfully transcribe the paper's equations, which is what `equations.tex` is for (see below), and whether the hypotheses of each theorem hold where the paper uses it, which the paper's Internet Appendix records result by result.

## Contents

| Path | What it is |
|:-----|:-----------|
| `lean/` | The Lean 4 project (`AILabProofs`). Eleven source files under `lean/AILabProofs/`, one per cluster of results. |
| `lean/README.md` | The complete theorem-by-theorem map from Lean names to paper propositions and equation labels, plus the precise scope (what is and is not formalized). |
| `equations.tex` | Every display equation of the paper and the Internet Appendix, in source order, each with its introducing prose and its equation label (e.g. `eq-trigger-phi`). Auto-generated from the manuscript source, so it cannot drift from the paper. |
| `Dockerfile`, `verify.sh` | A self-contained verification environment: build the image and it installs Lean, downloads the prebuilt Mathlib, and kernel-checks every proof; running it prints the axiom report. Needs only Docker on the host (see [How to execute it](#how-to-execute-it)). |

## What is verified

Identities and inequalities under stated hypotheses, conditional on the functional forms, exercise payoffs, and value matching and smooth pasting conditions that the paper derives:

- the reduction of the homogeneous Euler ODE to the characteristic equation, and the characteristic roots with their ordering (`EulerODE.lean`, `CharacteristicRoots.lean`);
- Proposition 1: the training-fraction first-order condition, its unique interior root `φ*` in closed form and its comparative statics (`Proposition1Phi.lean`); the post-switch trigger and NPV, the capacity first-order condition and its closed form `K_H*`, positive under (A2) and the unique global maximiser of the reduced capacity objective (`Proposition1.lean`, `Capacity.lean`); the particular solutions of the pre-switch problem and the equivalence of its first-order conditions with smooth pasting and the scale condition (`PreSwitch.lean`);
- Proposition 2: smooth pasting on the equity value equivalent to the closed-form default boundary, the shutdown boundary and continuity in leverage, the faith-based survival threshold and its comparative statics, and the default-boundary monotonicities (`Proposition2.lean`); identities of the recovery rule at the optimal allocation (`Credit.lean`);
- Corollary 1: the first and second derivatives of installed value in the arrival rate, monotonicity and strict concavity iff `φ > φ̲`, and the news identity (`Corollary1.lean`);
- Proposition 3: the contest algebra behind the allocation condition, uniqueness of the root of the follower's capacity condition, and the algebra of the values before the first investment; plus two generic lemmas about the nested pure-power game (`Duopoly.lean`).

No theorem proves that a policy is optimal in its stopping problem, that an equilibrium exists or is unique, or any number in the paper.

Results are stated for abstract parameters under the paper's admissibility
assumptions, so each theorem holds for *every* admissible parameter value,
not just the baseline calibration.

**What this package is not.** It is the *proof* package only. The numerical
results (triggers, equilibria, the robustness sweep, the piecewise and
coupled-boundary verifications, and every figure and table) are produced by
the Python code in the public repository, whose test suite pins the printed
numbers; the Internet Appendix refers to that repository, not to this zip,
wherever it says a check is enforced automatically. A self-contained
numerical supplement (source, `pyproject.toml` and `uv.lock`, configuration,
and the commands behind each exhibit) can be assembled from the repository
with `just build-replication-package` extended accordingly, and will be
archived with the paper upon publication.

**Not formalized** (see `lean/README.md` for the precise list): the derivation of the HJB equations from stochastic-calculus primitives and every optimal-stopping verification argument, including the optimality of the default rule (taken as the starting point, as in the paper's appendix); the pre-switch two-region system as a whole and the waiting margin; the pure-power (`A₁ = 0`) approximation; the single-boundary reduction of the credit block and the recovery caps; existence of a root of the follower's condition; the entry equilibrium of the duopoly; and all numerical results. Numerical results are reproducible from the public code repository: <https://github.com/fintech-research/ai-lab-investment/>.

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

### Option A — Docker (recommended; nothing to install but Docker)

From the package root (the directory containing the `Dockerfile` and `lean/`):

```bash
docker build -t ail-proofs .   # installs Lean, downloads prebuilt Mathlib,
                               # and kernel-checks every proof
docker run --rm ail-proofs      # prints the axiom report for the headline theorems
```

The build downloads the prebuilt Mathlib (~2–3 GB) and then compiles the
proofs; it takes a few minutes on a fast connection. **A successful `docker
build` is itself the verification** — the build fails if any proof is broken.
The `docker run` step re-confirms the build and prints, for one headline
theorem per source file, the axioms it depends on (expected: `propext`,
`Classical.choice`, `Quot.sound` only — no `sorryAx`).

### Option B — Native (Lean toolchain on the host)

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

The same axiom report for every headline theorem, plus a `sorry` scan, is
produced by `bash verify.sh` (this is what the Docker image runs).

---

*Package maintainers: `equations.tex` is generated by `extract_equations.py`
from the paper's Quarto sources — regenerate it (`just
build-replication-package` from the repository root) rather than editing it.*
