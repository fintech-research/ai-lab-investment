# Declaration of generative AI and AI-assisted technologies

<!-- Generic disclosure accompanying journal submissions. The short-form
     statement below follows the Elsevier template (required in-manuscript,
     before the references, for Elsevier targets: JCF, JEDC, JIFMIM, IRFA);
     the long form provides the detail for cover letters, submission portals,
     or journals with broader disclosure requirements (e.g., Management
     Science / INFORMS). -->

## Short-form statement (for the manuscript)

During the preparation of this work the author used generative AI tools — principally Claude and Claude Code (Anthropic), with additional use of ChatGPT and Codex (OpenAI), Gemini (Google), and the Refine.ink review platform — to draft and revise text, derive and check mathematical results, write analysis and figure-generation code, and review the manuscript. All mathematical results were independently verified, including a machine-checked formalization of the paper's closed-form derivations in Lean 4 / Mathlib. After using these tools, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article.

## Detailed disclosure

### Scope of AI assistance

AI assistance was used extensively throughout this project, in the following capacities:

- **Writing.** Generative AI tools drafted and revised manuscript text under the author's direction. The author set the research question, the model structure, and all key conceptual decisions; reviewed every draft; and made or approved all substantive choices.
- **Mathematical derivations.** AI tools assisted in deriving the model's closed-form results. All derivations were verified through three independent channels: symbolic verification in SymPy, numerical verification in Python, and formal verification in Lean 4 against the Mathlib library. The Lean formalization machine-checks the characteristic roots, boundary conditions, first-order conditions, comparative statics, and the existence and uniqueness of the preemption trigger, with no unproven assumptions (`sorry`-free, standard axioms only).
- **Code and figures.** The analysis pipeline and all figures were produced with AI-assisted code, which is publicly available and tested.
- **Reference verification.** References were checked against original sources with AI-assisted web browsing; one AI-suggested reference found to be inaccurate during this process was removed.
- **Review.** Multiple AI systems (Claude, ChatGPT, Codex, Gemini, Refine.ink) were used as complementary reviewers across successive revision rounds, alongside human feedback.

### Tools used

Claude and Claude Code (Anthropic); ChatGPT and Codex (OpenAI); Gemini (Google); Refine.ink (AI-assisted peer review platform).

### Transparency and responsibility

The complete development history of this paper — every draft, derivation, and revision — is publicly available in the project's GitHub repository (<https://github.com/fintech-research/ai-lab-investment/>). The genesis of the project is described in a public blog post (<https://vincent.codes.finance/posts/vibe-research-paper/>).

The author directed all stages of the research, reviewed and edited all AI-generated content, and takes sole and full responsibility for the integrity and content of the work, including any errors.
