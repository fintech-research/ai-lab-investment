# AI Workflow Description

## Overview

AI tools were used extensively throughout all stages of this project, from
initial conception through model development, code implementation, paper
writing, and revision. The full project history (238 commits over approximately
four weeks) is publicly available at
<https://github.com/fintech-research/ai-lab-investment>, and a detailed
account of the process is documented in a companion blog post at
<https://vincent.codes.finance/posts/vibe-research-paper/>.

## Tools Used

- **Claude Code** (Anthropic) was the primary tool, used for code
  development, paper drafting, mathematical derivations, and iterative
  revisions. The majority of commits (165 of 203 non-merge commits) are
  co-authored with Claude Opus 4.6 or Claude Sonnet 4.6.
- **Claude.ai** with research mode was used for literature surveys,
  calibration data gathering, and exploring the initial research plan.
- **ChatGPT** (OpenAI), **Codex CLI** (OpenAI), and **OpenCode with Gemini**
  (Google) were used as independent reviewers, generating parallel referee
  reports that were then consolidated and addressed.
- **Claude Cowork** and **Refine** were used for reference verification and
  structured peer review feedback.

## Workflow

The project followed an iterative cycle of AI-assisted drafting and
human-directed revision:

1. **Conception and planning.** The initial research question, model
   structure, and paper outline were developed through conversation with
   Claude's research mode, drawing on the author's expertise in corporate
   finance and real options.

2. **Model development and implementation.** The mathematical model
   (regime-switching real options with duopoly preemption, endogenous default,
   and training-inference allocation) was developed iteratively. Claude Code
   wrote the Python implementation, symbolic verification (SymPy), and
   numerical solvers, with the author directing the model architecture and
   verifying economic intuition at each stage. The project was built in
   phases: single-firm base model, duopoly with default risk, calibration,
   valuation analysis, and paper writing.

3. **Paper writing.** All sections were drafted by AI, with the author
   providing direction on framing, emphasis, and narrative structure. The
   paper was written in Quarto (markdown to PDF) with figures generated
   programmatically in Python.

4. **Review and revision.** Multiple independent AI agents (Claude, ChatGPT,
   Gemini) were used to generate parallel referee reports, simulating a
   multi-reviewer process. The author consolidated the feedback, decided which
   comments to address, and directed revisions. This review cycle was repeated
   multiple times.

5. **Verification.** References were independently verified using Claude
   Cowork and web searches. Mathematical derivations were cross-checked with
   SymPy symbolic computation. Numerical results were validated through
   parameter sweeps and robustness checks.

## Role of the Author

The author provided research direction, economic judgment, and quality
control throughout. Key decisions, including the model specification, which
results to emphasize, how to frame contributions, and which reviewer
suggestions to accept or reject, were made by the author. AI made the
project faster by lowering the cost of exploring ideas, writing code, and
iterating on prose, but the research taste, domain expertise, and strategic
direction came from the author.

## Transparency

Every AI-assisted commit in the repository includes a `Co-Authored-By` tag
identifying the model used. The full conversation logs, git history, and
blog post provide a complete audit trail of the human-AI collaboration.
