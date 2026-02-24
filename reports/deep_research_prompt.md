# Deep Research Prompt: AI Lab Investment Data Collection

## Context

I am writing an academic finance paper titled "Investing in Artificial General Intelligence" that models irreversible capacity investment by AI labs under demand uncertainty with regime switching, oligopoly competition, endogenous default, and diminishing returns calibrated to AI scaling laws. The paper uses a stylized calibration with four firm archetypes (Anthropic-like, OpenAI-like, Google/Alphabet-like, xAI-like) and needs up-to-date data from public sources.

The calibration is intentionally *stylized* -- I need order-of-magnitude figures and credible ranges, not precise structural estimates. However, the current numbers in the paper are potentially outdated (sourced in late 2024 / early 2025) and need to be verified or updated against the latest available information as of early-to-mid 2026.

Below are the specific data points I need, organized by topic. For each item, please provide: (a) the best current estimate with a credible range, (b) the primary source (earnings call, filing, press report, analyst estimate), and (c) the date of the source.

---

## 1. Revenue Data (AI-Related Revenue)

For each of the following companies, provide estimated AI-related revenue for 2024 (actual) and 2025 (actual or latest estimate), along with 2026 projections if available. Where the company is diversified, I need the AI-specific or cloud-specific revenue segment, not total corporate revenue.

### 1.1 Anthropic
- Annual revenue (or annualized revenue run-rate, ARR) for 2024 and 2025.
- Any public statements by Dario Amodei or other executives about revenue trajectory, revenue targets, or path to profitability.
- Sources: press reports, investor presentations, funding round disclosures.

### 1.2 OpenAI
- Annual revenue (or ARR) for 2024 and 2025.
- Revenue breakdown if available: ChatGPT subscriptions, API revenue, enterprise contracts.
- Any public statements by Sam Altman or other executives about revenue trajectory.
- Reported or estimated losses / burn rate.
- Sources: press reports (The Information, Bloomberg, WSJ, NYT), investor materials.

### 1.3 Google / Alphabet (Google Cloud + AI)
- Google Cloud revenue for 2024 and 2025 (from 10-K / 10-Q filings).
- Any breakdown of AI-specific vs. traditional cloud revenue within Google Cloud.
- DeepMind-related revenue or cost attribution if disclosed.
- Sources: SEC filings (10-K, 10-Q), earnings call transcripts.

### 1.4 xAI
- Any reported revenue figures for 2024 and 2025 (Grok API, Grok subscriptions, X platform integration revenue).
- Impact of the March 2025 merger with X (Twitter) on revenue attribution.
- Sources: press reports, investor disclosures, Elon Musk public statements.

### 1.5 Other Major Players (for context/comparison)
- **Microsoft** (Azure AI / Copilot revenue): AI-related revenue or Azure AI segment for 2024-2025.
- **Amazon** (AWS AI / Bedrock): AI-related revenue within AWS for 2024-2025.
- **Meta** (Llama / AI infrastructure spending): Any disclosed AI revenue or cost figures.
- **Mistral, Cohere, AI21, Inflection**: Revenue estimates if available.
- **DeepSeek**: Any financial information, funding, estimated costs.

---

## 2. Capital Expenditure Data

For each of the four archetype companies and the major comparables, provide CapEx figures for 2024 (actual) and 2025 (actual or latest guidance), with 2026 guidance if available. I need CapEx specifically related to AI infrastructure (data centers, GPUs, networking) where possible.

### 2.1 Anthropic
- Total CapEx or infrastructure spending for 2024 and 2025.
- Fundraising rounds and their stated purpose (e.g., compute procurement, data center leases).
- Any cloud compute agreements (e.g., with Google Cloud, AWS).

### 2.2 OpenAI
- Total CapEx or infrastructure spending for 2024 and 2025.
- Stargate Project: committed capital, timeline, partners (SoftBank, Oracle, MGX), amount actually deployed vs. announced.
- Other infrastructure commitments (Azure partnership, custom chips).

### 2.3 Google / Alphabet
- Total CapEx for 2024 and 2025 (from filings). What portion is attributable to AI / data centers?
- Any public guidance on 2026 CapEx.
- TPU investment and custom silicon strategy.

### 2.4 xAI
- Colossus supercluster: total investment, GPU count (reported 230k H100s, then expansion plans to 550k+).
- Total estimated CapEx for 2024 and 2025.
- Funding rounds and valuations.

### 2.5 Other Major Players
- **Microsoft**: Total CapEx and AI-specific CapEx for 2024-2025. Any breakdown between Azure capacity and OpenAI support.
- **Amazon/AWS**: Total CapEx and AI-related portion for 2024-2025. Custom chip investments (Trainium, Inferentia).
- **Meta**: Total CapEx and AI-related portion for 2024-2025. Llama training costs, data center buildout.
- **NVIDIA**: Revenue as a proxy for industry GPU spending. Data center segment revenue for 2024-2025.

### 2.6 Industry Aggregates
- Total AI infrastructure CapEx across the industry for 2024, 2025, and 2026 (projected).
- The most recent update to the Sequoia "$600B question" analysis (David Cahn, 2024): has the revenue gap narrowed? Any updated estimates?
- Any analyst estimates of total AI CapEx vs. AI revenue for the industry.

---

## 3. GPU Fleet Sizes and Compute Capacity

For each archetype company, provide estimated GPU fleet sizes (or equivalent compute capacity in FLOPs):

- **Anthropic**: Estimated GPU count (H100/B200 equivalent), cloud vs. owned.
- **OpenAI**: Estimated GPU count, Azure allocation, owned vs. leased.
- **Google**: TPU fleet size (v4, v5, Trillium) and/or GPU equivalents.
- **xAI**: Colossus cluster details (230k H100s confirmed, expansion to 550k+?). Colossus 2 status.
- **Meta**: GPU fleet for Llama training and inference.
- **Microsoft**: Total GPU fleet for Azure AI.
- **Amazon**: GPU/Trainium fleet for AWS AI.

Also provide:
- Current GPU pricing: H100, H200, B200, GB200/GB300. Any price trends.
- Estimated cost per GW-year of data center capacity (Dario Amodei estimated $10-15B -- is this still current?).
- Data center build timelines: how long from announcement to operational for a large AI data center?

---

## 4. Training vs. Inference Compute Allocation

This is one of the most important and hardest-to-source data points for the paper. I need estimates of what fraction of total compute each company allocates to model training vs. inference serving.

### 4.1 Direct Statements
- Any public statements by executives about their training vs. inference split.
- Dario Amodei's statements about compute allocation (he has discussed this on the Dwarkesh Patel podcast and elsewhere).
- Jensen Huang's statements about the training-to-inference ratio shift.

### 4.2 Analyst Estimates
- Bernstein, Morgan Stanley, Coatue, or other analyst estimates of the industry-wide training vs. inference split.
- How has this ratio evolved from 2023 to 2025/2026? Is inference growing as a share?

### 4.3 Indirect Evidence
- GPU utilization data from cloud providers (training clusters vs. inference endpoints).
- Inference-time compute scaling (OpenAI o1/o3, "test-time compute"): how does this affect the training/inference boundary?
- Is there a convergence between training and inference (e.g., reinforcement learning from human feedback, online learning)?

### 4.4 Current Estimates by Company
My current estimates (which need verification/updating):
- Anthropic-like: 60% training
- OpenAI-like: 55% training
- Google-like: 40% training (large inference workload)
- xAI-like: 80% training (Colossus dedicated to training, inference outsourced)

Are these still reasonable? What would updated estimates be?

---

## 5. Executive Statements on AGI Timelines and Beliefs

The paper uses a "revealed beliefs" methodology that maps observed investment behavior to implied beliefs about the probability and timing of transformative AI. I need up-to-date executive statements about AGI timelines.

### 5.1 Specific Executives
For each person below, find their most recent public statements (2025-2026) about AGI timelines, AI progress, or the expected return on AI investment:

- **Dario Amodei** (Anthropic CEO): Especially the February 2026 Dwarkesh Patel interview about the "cone of uncertainty" in AI investment. Also his October 2024 "Machines of Loving Grace" essay and any subsequent updates.
- **Sam Altman** (OpenAI CEO): His "Three Observations" (Feb 2025) and any subsequent statements. Any statements about AGI timeline, investment strategy, or the Stargate project.
- **Sundar Pichai** (Google/Alphabet CEO): Earnings call statements about AI investment risk/return. His "risk of underinvestment" framing.
- **Jensen Huang** (NVIDIA CEO): GTC 2025 keynote and subsequent statements about scaling, inference scaling, and the AI compute buildout.
- **Elon Musk** (xAI): His January 2026 "achieve AGI in 2026" post and any clarification. Statements about Colossus and xAI's strategy.
- **Satya Nadella** (Microsoft CEO): His "economic test for AGI" framework and statements about the return on AI infrastructure investment.
- **Andy Jassy** (Amazon CEO): His February 2026 earnings call confidence in $200B spending plan.
- **Mark Zuckerberg** (Meta CEO): Statements about open-source AI investment (Llama) and Meta's AI CapEx plans.
- **Demis Hassabis** (Google DeepMind CEO): His March 2025 "human-level AI in 5-10 years" statement and any updates.
- **Yann LeCun** (Meta Chief AI Scientist): His skeptical view on autoregressive LLMs reaching human-level intelligence (CES 2025 and subsequent).
- **Ilya Sutskever** (SSI / formerly OpenAI): His December 2024 NeurIPS remarks on pre-training scaling hitting a wall.
- **Noam Brown** (OpenAI): Statements about inference-time compute scaling (o1/o3).

### 5.2 Key Themes to Capture
- The dispersion in beliefs (optimists vs. skeptics) and how it maps to investment behavior.
- The "risk of underinvestment vs. risk of overinvestment" framing (Pichai, Amodei, Nadella).
- Any quantitative statements about probability of AGI, expected timelines, or confidence intervals.
- Statements about whether scaling laws are "hitting a wall" or continuing to hold.
- The shift from pre-training scaling to inference-time scaling / test-time compute.

---

## 6. Financial Parameters

### 6.1 Cost of Capital / WACC
- Current WACC estimates for major tech/AI companies (2025-2026).
- Damodaran industry WACC data for the technology sector, if updated.
- Cost of equity for pure-play AI labs (Anthropic, OpenAI) vs. diversified tech (Google, Microsoft).
- Are AI labs paying a premium for capital? How has this evolved?

### 6.2 Leverage and Capital Structure
- Anthropic: total debt (venture debt, credit facilities), debt-to-capital ratio.
- OpenAI: credit facilities, convertible notes, the restructuring to for-profit. Total debt load.
- Google: corporate debt levels (from balance sheet), debt-to-capital.
- xAI: funding structure, any debt instruments, valuation.
- Are AI labs using more or less leverage than in 2024? Any new debt instruments or structures?

### 6.3 Cost of Debt
- Typical coupon rates on AI company debt (venture debt, credit facilities, convertible notes).
- Any bond issuances by AI-adjacent companies.
- Credit spreads for AI/tech companies.

---

## 7. Scaling Laws and Diminishing Returns

### 7.1 Updates to Scaling Laws
- Any new empirical results on compute scaling laws since Hoffmann et al. (2022)?
- Evidence for or against "scaling law plateaus" or diminishing returns at frontier scale.
- New scaling paradigms: inference-time compute scaling (o1, o3), chain-of-thought, test-time compute.
- DeepSeek's efficiency claims: what do they imply for scaling economics?

### 7.2 Revenue Elasticity of Compute
- Any empirical evidence on how additional compute capacity translates to revenue (the $\alpha$ parameter in the paper)?
- GPU utilization rates at major cloud providers.
- Inference demand elasticity: how price-sensitive is AI inference demand?

### 7.3 Operating Costs
- Power costs for large data centers ($/kWh at hyperscale).
- Cooling and maintenance costs as a fraction of infrastructure value.
- Has the "operating cost rate" changed with newer GPU generations (B200 vs. H100)?
- Power availability constraints and their impact on buildout timelines.

---

## 8. Industry Structure and Competition

### 8.1 Market Concentration
- Market share estimates for AI model providers (API market, enterprise AI).
- Is the market consolidating or fragmenting?
- Role of open-source models (Llama, Mistral, DeepSeek) in the competitive landscape.

### 8.2 Revenue Gap Analysis
- Update on the Sequoia "AI's $600B Question" (Cahn 2024): has the gap between AI infrastructure CapEx and AI revenue narrowed?
- Other analyst estimates of the AI investment-to-revenue ratio.
- Is there evidence of AI revenue catching up to investment, or is the gap widening?

### 8.3 Strategic Dynamics
- Any evidence of preemption behavior (investing to deter competitors)?
- Examples of firms slowing or accelerating investment in response to competitors.
- The impact of DeepSeek R1 (January 2025) on investment strategies: did it cause any firms to reconsider?

---

## 9. Additional Data Points

### 9.1 Bankruptcy / Financial Distress Risk
- Any AI companies that have faced financial distress, down rounds, or significant layoffs.
- Stability AI as a case study: what happened?
- Inflection AI: what happened after Microsoft hired key staff?
- Any analyst commentary on the financial sustainability of current AI investment levels.

### 9.2 Time-to-Build
- Typical timelines for large AI data center projects (from announcement to operational).
- Examples of fast-tracked projects (e.g., Colossus built in ~120 days).
- Supply chain constraints for GPUs, networking equipment, power infrastructure.

### 9.3 Regulatory and Policy
- Any new regulations affecting AI infrastructure investment (export controls, power regulations, zoning).
- Government subsidies or incentives for AI infrastructure (CHIPS Act, international equivalents).

---

## Output Format

Please organize your findings as follows:

1. **Summary table** updating my current firm archetype data (revenue, CapEx, GPU count, leverage, WACC, training fraction) with the latest available numbers.

2. **Detailed findings** organized by the sections above, with specific sources and dates.

3. **Key uncertainties** -- where data is particularly unreliable or contested, flag it explicitly.

4. **Timeline of executive statements** on AGI/AI timelines, organized chronologically (2024-2026), with direct quotes where available.

5. **Suggested parameter updates** for my model calibration, with justification.

Thank you.
