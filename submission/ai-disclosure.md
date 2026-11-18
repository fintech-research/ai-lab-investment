# Declaration of generative AI and AI-assisted technologies

<!-- Generic disclosure accompanying journal submissions. The short-form
     statement below follows the Elsevier template (required in-manuscript,
     before the references, for Elsevier targets: JCF, JEDC, JIFMIM, IRFA);
     the long form provides the detail for cover letters, submission portals,
     or journals with broader disclosure requirements (e.g., Management
     Science / INFORMS). -->

## Short-form statement (for the manuscript)

During the preparation of this work the author used generative AI tools — principally Claude and Claude Code (Anthropic), with additional use of ChatGPT and Codex (OpenAI), Gemini (Google), and the Refine.ink review platform — to draft and revise text, derive and check mathematical results, write analysis and figure-generation code, and review the manuscript. The closed-form mathematical results were checked symbolically and numerically, and parts of their algebra and calculus are formalized and machine-checked in Lean 4 / Mathlib; the paper's Internet Appendix lists what is and is not formalized. After using these tools, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article.

## Detailed disclosure

### Scope of AI assistance

AI assistance was used extensively throughout this project, in the following capacities:

- **Writing.** Generative AI tools drafted and revised manuscript text under the author's direction. The author set the research question, the model structure, and all key conceptual decisions; reviewed every draft; and made or approved all substantive choices.
- **Mathematical derivations.** AI tools assisted in deriving the model's closed-form results. The closed-form derivations were checked in three ways: symbolically in SymPy, numerically in the Python test suite, and formally in Lean 4 against the Mathlib library. The three checks share the model's equations as their input, so they are complementary rather than statistically independent, and they verify algebra and calculus, not the economic hypotheses of the results, which the paper's Internet Appendix records result by result. The Lean formalization covers parts of the algebra and single-variable calculus that follow once the stopping problems are set up, each stated as an identity or inequality under explicit hypotheses: the reduction of the homogeneous Euler ODE to the characteristic equation and the sign and ordering of its roots; the training-fraction first-order condition, its closed form and comparative statics; the post-switch trigger, the capacity first-order condition, the positivity of its closed form and the global optimality of the post-switch capacity in its reduced objective; the particular solutions and first-order conditions of the pre-switch problem; the equivalence of smooth pasting with the closed-form default boundary, the faith-based survival condition and threshold with its comparative statics, and the default-boundary monotonicities; identities of the recovery rule at the optimal allocation; the installed value in the arrival rate (Corollary 1); and, for the duopoly, the contest algebra behind the allocation condition, uniqueness of the root of the follower's capacity condition, and the algebra of the values before the first investment. Every theorem is proved in full, with no unproved placeholders (`sorry`-free) and only Lean's standard axioms, which means no gaps in the formal proofs, not the absence of economic hypotheses. Outside the formalization are the stochastic-calculus derivation of the Hamilton–Jacobi–Bellman equations, every optimal-stopping verification argument (including the optimality of the default rule), the pre-switch two-region system as a whole, the pure-power (A₁ = 0) approximation, the entry equilibrium of the duopoly, and every result that is numerical in nature (among them the magnitude of the net threshold, the credit spreads and default probabilities, and the coupled-ODE, piecewise-stopping, entry-game, and Dario's-dilemma computations). The paper's Internet Appendix states this scope in the same terms.
- **Code and figures.** The analysis pipeline and all figures were produced with AI-assisted code, which is publicly available and tested.
- **Reference verification.** References were checked against original sources with AI-assisted web browsing; one AI-suggested reference found to be inaccurate during this process was removed.
- **Review.** Multiple AI systems (Claude, ChatGPT, Codex, Gemini, Refine.ink) were used as complementary reviewers across successive revision rounds, alongside human feedback.

### Tools used

Claude and Claude Code (Anthropic); ChatGPT and Codex (OpenAI); Gemini (Google); Refine.ink (AI-assisted peer review platform).

### Transparency and responsibility

The complete development history of this paper — every draft, derivation, and revision — is publicly available in the project's GitHub repository (<https://github.com/fintech-research/ai-lab-investment/>). The genesis of the project is described in a public blog post (<https://vincent.codes.finance/posts/vibe-research-paper/>).

The author directed all stages of the research, reviewed and edited all AI-generated content, and takes sole and full responsibility for the integrity and content of the work, including any errors.
