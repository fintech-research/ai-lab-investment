# Cover letter — Management Science

<!-- Currently targeted at Management Science (first journal on the ladder in
     submission/README.md). To retarget: update the salutation, journal name,
     and the fit paragraph. -->

Dear Editor,

I am pleased to submit my manuscript, "Investing in Artificial General Intelligence," for consideration at *Management Science*.

The paper develops a real-options model of irreversible capacity investment by frontier AI laboratories. A firm facing regime-switching demand, duopoly competition, and endogenous default must decide when to invest, how much compute capacity to install, and how to split that capacity between inference (current revenue) and training (future capability). The central contribution is the characterization of a training–survival channel: because the same capacity serves both current revenue and future capability, the allocation decision links the firm's growth option to its default boundary. This produces a "faith-based survival" mechanism, in which training investment lowers the default boundary by raising the expected post-AGI continuation value, and an asymmetric cost of mistaken beliefs about AI timelines — conservative underinvestment is costlier in expected value, while aggressive overinvestment concentrates tail default risk. The model delivers closed-form investment triggers and a semi-analytical duopoly preemption equilibrium, calibrated to four AI-lab archetypes.

I believe *Management Science* is the natural home for this work. The paper sits at the interface of finance and operations that the journal has long cultivated: it embeds a capacity-allocation problem — how to divide irreversible compute capacity between revenue-generating inference and capability-building training — inside a dynamic corporate finance model with strategic competition and endogenous default, building directly on the real-options and strategic capacity-investment tradition the journal's audience has shaped. The economics of AI infrastructure investment should interest readers across the finance, operations, and strategy areas; I would suggest the Finance department as the most natural fit for evaluation.

I want to be fully transparent about the role of AI in this project, which is by now widely known in the profession: this paper began as a heavily AI-assisted experiment, and the first days of work are documented publicly in a blog post, "Vibe Research, or How I Wrote an Academic Paper in Four Days" (<https://vincent.codes.finance/posts/vibe-research-paper/>). The complete development history, including all AI tooling used, is available in the paper's public GitHub repository (<https://github.com/fintech-research/ai-lab-investment/>). The manuscript has since gone through extensive rounds of review and revision. I stand fully behind the paper, and I take sole responsibility for any errors it may contain. A detailed disclosure statement accompanies this submission.

I am mindful that refereeing a theory-heavy paper is time-consuming. To ease the verification burden, the submission includes a Lean 4 / Mathlib validation package that machine-checks the paper's closed-form derivations — the characteristic roots, value-matching and smooth-pasting conditions, first-order conditions, comparative statics, and the existence and uniqueness of the preemption trigger; that is, the algebraic steps a referee would otherwise check by hand. Every theorem is verified by the Lean kernel with no unproven assumptions. All numerical results are separately reproducible from the public repository. The referee can therefore focus on the economics rather than the algebra.

Finally, because the manuscript is already publicly available — both on SSRN (<https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6305300>) and as raw source in the public GitHub repository — the confidentiality considerations that normally counsel against uploading a manuscript to cloud AI services do not apply. To the extent that the journal's own policies permit it, I explicitly grant referees permission to upload the manuscript to services such as ChatGPT or Claude if they find AI assistance useful in their review.

This manuscript is original, is not under consideration elsewhere, and has not been previously published. I have no conflicts of interest to declare.

Thank you for your consideration.

Sincerely,

Vincent Grégoire
HEC Montréal
vincent.gregoire@hec.ca
