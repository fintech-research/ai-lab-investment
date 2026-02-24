# Data Compendium: Investing in Artificial General Intelligence

**Prepared for:** Vincent Grégoire, HEC Montréal
**Date:** February 24, 2026
**Purpose:** Stylized calibration data for "Investing in Artificial General Intelligence" — order-of-magnitude figures and credible ranges from public sources.

---

## Overview

The AI infrastructure buildout has accelerated far beyond late-2024 projections. Combined hyperscaler CapEx guidance for 2026 now exceeds **$660 billion** — roughly triple 2024 levels [1][2] — while frontier AI lab revenues have grown 5–10× in just 18 months. The gap between infrastructure spending and AI revenue remains enormous, but the speed of revenue growth (Anthropic: $1B → $14B ARR in 14 months; OpenAI: $6B → $20B ARR in 12 months) is narrowing the ratio faster than most analysts expected. Below is a comprehensive, sourced data compendium organized to support calibration of the paper's four firm archetypes.

---

## 1. Revenue Data

### 1.1 Anthropic

Anthropic's revenue trajectory has been the most dramatic growth story in AI. The company reached **$1B ARR in December 2024**, then accelerated to **$14B ARR by February 12, 2026** — a roughly 10× annual growth rate sustained for three consecutive years [3]. Calendar-year 2024 collected revenue was approximately **$400–600M** (since ARR extrapolates the most recent month), while 2025 collected revenue was an estimated **$4–5B**. Dario Amodei told CNBC in January 2026 that Anthropic generated "close to $10 billion in revenue last year," though this likely conflates ARR with collected revenue [5].

The revenue mix skews heavily enterprise: roughly **70–75% from pay-per-token API calls**, 10–15% from consumer subscriptions (Claude Pro at $20/month, Claude Max at $100–200/month), and the remainder from enterprise contracts and reserved capacity [6][7]. Some **80% of revenue comes from business customers** — over 300,000 as of October 2025. Claude Code alone reached **$2.5B ARR** by February 2026 [3]. Internal projections target **$20–26B ARR by end of 2026** and $70B in revenue by 2028 [8][9]. The company expects gross margins to reach 50% in 2025 and 77% by 2028, with break-even projected for **2028** [8]. Cash burn was $5.6B in 2024 and targeted at $3B in 2025 [10].

**Funding and valuation trajectory:**

- Series E: $2B (October 2024, Amazon-led)
- Series F: $13B (September 2025, $183B valuation) [11]
- Series G: **$30B** (February 12, 2026, **$380B valuation**) — second-largest private tech round in history [12][13]
- Total raised: ~$64B [14]
- Key investors: Amazon ($8B total), Google (~$3B), Microsoft (up to $5B), NVIDIA (up to $10B) [5][15]

### 1.2 OpenAI

OpenAI's ARR grew from **$6B at end of 2024** to **$20B by December 2025**, with the company hitting its first $1B revenue month in July 2025. CFO Sarah Friar confirmed these milestones in a January 18, 2026 blog post [4][16]. Calendar-year 2025 collected revenue was approximately **$12–13B** (up from ~$3.7B in 2024) [17]. Sam Altman stated revenue was "well more" than the $13B target.

Revenue breaks down approximately **75% ChatGPT subscriptions** (Plus, Pro, Team, Enterprise — with ~15M active subscribers as of mid-2025 and 1M+ organizations by December 2025), ~20–25% API revenue, and a nascent advertising component tested in January 2026. Notably, The Information reported that Anthropic's API revenue ($3.8B) was roughly **2× OpenAI's API revenue ($1.8B)** in 2025 [18], suggesting OpenAI's consumer subscription business is the primary revenue engine. OpenAI projects **$29–30B in 2026 revenue** and $200–280B by 2030 [19][20].

**Losses and burn rate:**

- 2024 net loss: ~**$5B** [21][22]
- H1 2025: $13.5B net loss (including non-cash items) on $2.5B actual cash burn [23]
- Projected 2026 loss: **$14B** [24]
- Cash position: ~$17.5B at mid-2025 [23]
- HSBC estimated a **$207B funding shortfall** to power growth plans through profitability [25]
- Profitability target: **2029–2030** [26]

**Corporate restructuring:** The for-profit conversion completed October 28, 2025, forming OpenAI Group PBC. Microsoft retained a 27% stake plus a $250B Azure purchase commitment [27][28].

**Funding rounds:**

- Series E: $6.6B (October 2024, $157B valuation, SoftBank/Thrive Capital-led) [29]
- $4B revolving credit facility (October 2024, JPMorgan-led, SOFR + 100bps) [30]
- Series F: $40B (March 2025, $300B valuation, SoftBank-led) [31]
- Reported February 2026: **$100B+ round** in progress at $730–830B valuation [32]

### 1.3 Google / Alphabet (Google Cloud + AI)

Google Cloud revenue from SEC filings: Full-year 2024 was **~$43.2B** (+31% YoY), accelerating to an estimated **$59–60B in 2025** (+37–39% YoY) [33][34]. Q4 2025 alone was **$17.66B** (+48% YoY), representing an annualized run rate exceeding **$70B** [33][35]. Operating margins expanded: Q4 2025 hit **30.1%** (up from 17.5% a year earlier), with operating income more than doubling to $5.3B [34][36].

Google Cloud backlog reached **$240B** at end of Q4 2025, up 55% sequentially and more than doubled YoY [36]. Fourteen product lines each exceeded $1B in annual revenue. The company does not separately disclose AI-specific vs. traditional cloud revenue, but management commentary attributes the acceleration to "enterprise AI Infrastructure and enterprise AI Solutions" [37]. Gemini models process **10 billion tokens per minute** via direct API use, and the Gemini App has **750 million monthly active users** [37].

Alphabet-level AI R&D spending (not allocated to segments) reached **$5.89B in Q4 2025 alone** — up 112% YoY — reflecting rapidly growing centralized AI investment, including DeepMind [36].

Full-year Alphabet revenue: **$403.3B** in 2025 (+16% YoY). Total revenue in 2024: ~$348B [34].

### 1.4 xAI

xAI's financial data carries the lowest confidence. Bloomberg (January 9, 2026) reported Q3 2025 revenue of **$107M** (nearly doubled QoQ) and cumulative 2025 revenue through September exceeding **$200M** [38][39]. Standalone xAI revenue reached an estimated **$500M annualized run rate** by year-end 2025 [40]. Morgan Stanley investor materials (June 2025) showed a **$1B 2025 revenue target** and projected positive EBITDA by 2027 and $14B revenue by 2029 [41].

The March 2025 all-stock merger with X (Twitter), valuing the combined entity at ~$113B, complicates revenue attribution. X's advertising revenue (~$2.9B annually in 2025) is now consolidated, producing a combined run rate of ~**$3.8B** [42][43]. Revenue streams include SuperGrok subscriptions ($30/month and $300/month tiers), the Grok API, and government contracts. xAI's burn rate was approximately **$1B per month** in 2025, with losses through September 2025 estimated at -$2.4B EBITDA [38][44].

**Key corporate event:** On February 2, 2026, **SpaceX acquired xAI in an all-stock transaction** valuing xAI at $250B within a combined $1.25T entity — the largest merger involving a private target in history [45][46].

**Funding rounds:**

- Series B: $6B (December 2024, $50B valuation) [47]
- Series C/D: $10B hybrid (July 2025, ~$200B) [48]
- Series E: **$20B** (January 2026, $230B valuation, NVIDIA/Cisco/Fidelity-led) [49][50]
- Total raised: >$42B in equity plus ~$5B in debt [44]

### 1.5 Other Major Players

**Microsoft:** Azure grew **39% in Q2 FY2026** (Oct–Dec 2025), with AI services contributing an estimated 22–26 percentage points. Azure surpassed a **$75B+ annual run rate**. Microsoft Cloud crossed $50B in a single quarter. M365 Copilot had 15M paid seats (+160% YoY) [51][52].

**Amazon/AWS:** Q4 2025 revenue of **$35.6B** (+24% YoY, fastest growth in 13 quarters), annualized ~$142B. AWS backlog: **$244B** (+40% YoY). Custom chips (Trainium + Graviton) crossed a **$10B+ ARR** [53][54].

**NVIDIA:** Data Center revenue FY2025 (ended Jan 2025): **$115.2B**. Through Q3 FY2026: **$131.4B** already (exceeding all of FY2025). Full FY2026 projected: ~$200–215B. Jensen Huang cited **$500B in Blackwell/Rubin revenue visibility** [55][56][57].

**Meta:** Q4 2025 ad revenue: $58.1B (+24% YoY). 2025 CapEx: ~$72B. 2026 CapEx guidance: **$115–135B** [58][59].

**Mistral:** ~€300M ARR by September 2025, targeting >€1B by end of 2026 [60].

**Cohere:** Crossed **$150M ARR** by October 2025 [61].

**DeepSeek:** ~$220M run rate by mid-2025. Self-funded by High-Flyer hedge fund with no external investors. Estimated 50K+ GPUs (H800/A100). Training cost for V3: ~$5.6M (final run only) [62][63].

---

## 2. Capital Expenditure Data

### 2.1 Anthropic

Rather than owning data centers historically, Anthropic committed to **$80B+ in cloud spending through 2029** across AWS, Google Cloud, and Azure [64][65]. AWS is the primary partner: ~$1.35B on AWS in 2024 and $2.66B through September 2025 [66]. The Google Cloud deal provides access to up to **1 million TPUs**, adding over 1 GW of compute capacity by 2026 [67][68]. The Microsoft Azure deal includes $30B in Azure credits.

Anthropic's first proprietary infrastructure push: a **$50B commitment to US AI infrastructure** (November 2025) via custom data centers with Fluidstack in Texas and New York [69][70].

### 2.2 OpenAI

Total committed infrastructure spending across seven vendors exceeds **$1.15 trillion** (2025–2035), including $250B incremental Azure, ~$300B Oracle (five-year), $38B AWS (seven-year), $22.4B CoreWeave, and massive AMD and Broadcom deals [71]. Actual Azure inference spending: ~**$3.8B in 2024** and $8.65B through Q3 2025 [72].

**Stargate Project** (announced January 21, 2025): **$500B over four years** via JV with SoftBank, Oracle, and MGX [73]. Abilene, Texas Phase 1 (2 buildings, 200+ MW) energized September 2025; Phase 2 (6 buildings, 1 GW) expected mid-2026 [74]. Five additional US sites announced September 2025 [75]. International sites span the UAE (1 GW), Norway, UK, Argentina. OpenAI compute capacity: 0.2 GW (2023) → 0.6 GW (2024) → ~1.9 GW (2025) [74].

In February 2026, OpenAI told investors its cumulative compute spending target is **~$600B by 2030**, with revenue projected at $280B by then [19].

### 2.3 Google / Alphabet

CapEx trajectory from SEC filings [34][76]:

| Year | Total CapEx | YoY Growth |
|------|-------------|------------|
| 2023 | $32.3B | — |
| 2024 | $52.5B | +62.5% |
| 2025 | $91.4B | +74% |
| 2026 (guidance) | **$175–185B** | ~+100% |

Initial 2025 guidance was $75B (February), revised to $85B (July) [77], then $91–93B (October) [78]. Q4 2025 CapEx was $17B alone [34][79]. Approximately **60% to servers** (GPUs, TPUs) and **40% to data centers and networking** [80]. FY2025 operating cash flow: **$164.7B**; free cash flow: **$73.3B** — CapEx is self-funded [34].

Custom silicon: seventh-generation **Ironwood TPU** for inference entering GA in FY2026 [81]. Google's power pipeline targets **2+ GW of energized capacity** by late 2026 [82].

### 2.4 xAI

**Colossus supercluster** (Memphis, Tennessee):

- Phase 1: 100,000 H100 GPUs deployed in **122 days** [83][84]
- Phase 2: ~200,000 GPUs (H100/H200/GB200) in an additional 92 days [85][86]
- **Colossus 2** (Southaven, Mississippi): targets **555,000 GB200/GB300 GPUs** at ~$18–20B for GPUs alone [87][88]
- Third building ("MACROHARDRR") announced December 2025 [89]
- Roadmap: **1 million GPUs**, **~2 GW** total power [90][91]

Estimated CapEx: ~$2.6B in 2024, **$10B+ in 2025** (given $7.8B cash burn through September) [38][92].

### 2.5 Other Major Players

**Microsoft:** Q2 FY2026 (Oct–Dec 2025) CapEx: **$22.6B** (single quarter). FY2026 annualized: ~$84–90B. Guided FY2026 total: potentially **$120B+**. CFO Amy Hood: "We are, and have been, short now for many quarters" [51][52].

**Amazon:** FY2025 CapEx: **$131.8B** (vs. $83B in 2024). FY2026 guidance: **~$200B** [53][93]. Andy Jassy (February 5, 2026): investment is "not some quixotic, top-line grab" [94].

**Meta:** FY2025 CapEx: ~$72B. FY2026 guidance: **$115–135B** (up from prior $60–65B 2025 guidance). Zuckerberg: 2026 will be "a big year for personal superintelligence" [58][95].

**NVIDIA:** Data Center revenue is the best proxy for industry GPU spending. FY2025: $115.2B. Q3 FY2026 alone: $50.4B (+112% YoY) [55][56].

### 2.6 Industry Aggregates

Combined hyperscaler CapEx estimates [1][2][96][97]:

| Year | Big 5 Hyperscalers | Notes |
|------|-------------------|-------|
| 2024 | ~$250–280B | Amazon $83B, Alphabet $52.5B, Microsoft ~$44.5B, Meta ~$40B |
| 2025 | ~$380–405B | Amazon $131.8B, Alphabet $91.4B, Microsoft ~$84B, Meta ~$72B |
| 2026 (guided) | **~$660–690B** | Amazon $200B, Alphabet $175–185B, Meta $115–135B, Microsoft ~$120B+ |

Goldman Sachs projected hyperscaler CapEx 2025–2027: **$1.15 trillion**, double the $477B from 2022–2024 [97]. McKinsey estimated global AI infrastructure spending: **$5.2 trillion over five years**. CapEx as share of operating cash flows: **94%** in 2025 (net of dividends/buybacks), up from 76% in 2024 [96]. Morgan Stanley/JP Morgan projected **$400B in new hyperscaler debt in 2026** alone [98].

---

## 3. GPU Fleet Sizes and Compute Capacity

### 3.1 Fleet Estimates (H100-equivalents, early 2026)

| Company | Estimated Fleet | Ownership Model | Confidence |
|---------|----------------|-----------------|------------|
| Anthropic | 800K–2M equiv. | ~100% cloud (AWS Trainium, Google TPU, Azure GPU); FluidStack DCs coming 2026 | Medium-low |
| OpenAI | 1M–1.5M equiv. | Primarily Azure; Stargate (Oracle); diversifying to AWS, CoreWeave | Medium |
| Google | 2M–3M equiv. | Mostly owned (TPU v4/v5/Trillium/Ironwood + NVIDIA GPUs) | Medium |
| xAI | 200K–555K GPUs | Owned (Colossus 1: ~200K deployed; Colossus 2: 555K targeted) | Medium-high (200K confirmed) |
| Meta | 600K–1M+ equiv. | Owned + cloud deals ($10B Google, $14.2B CoreWeave, $3B Nebius) | Medium-high |
| Microsoft | 1M–2M equiv. | Owned for Azure (400+ data centers); power-constrained | Medium |
| Amazon/AWS | 1M–2M equiv. (incl. 1.4M+ Trainium) | Owned; 6 GW installed, targeting 12 GW by 2027 | Medium |

A November 2024 LessWrong analysis by CharlesD remains the most methodologically transparent public estimate [99][100]. Sam Altman stated in July 2025 that OpenAI was on track for "well over" 1 million GPUs by year-end, and projected a need for **100 million GPUs for AGI** [101].

### 3.2 GPU Pricing (early 2026)

| GPU | Purchase Price | Cloud Rate (on-demand) |
|-----|---------------|----------------------|
| H100 SXM | $25,000–$40,000 | $1.50–$3.93/GPU-hr (fell 64–75% since early 2024) |
| H200 | $30,000–$40,000 | $2.50–$10.60/GPU-hr |
| B200 | $30,000–$35,000 | ~$6.25/GPU-hr |
| GB200 NVL72 rack | ~$3M per rack (72 GPUs) | $10.50–$20.14/GPU-hr |
| GB300 NVL72 rack | >$3M per rack | Pricing emerging |

H100 cloud prices dropped from **$8–10/hr (early 2024) to $2.85–$3.50/hr (late 2025)** as supply expanded [102][103]. Volume discounts of 30–70% are typical for 1–3 year commitments.

### 3.3 Data Center Cost per GW

Amodei's estimate of **$10–15B per GW** represents the **annualized operating + amortized cost**, not pure construction CapEx [104]. Full construction CapEx per GW varies:

- **Bernstein Research**: ~$35B/GW total [105]
- **NVIDIA estimate**: $50–60B/GW (future GPU cycles) [105]
- **AWS realized cost**: ~$29.5B/GW ($115B ÷ 3.9 GW added in 2025) [106]
- **McKinsey**: ~$40B/GW ($5.2T ÷ 125 GW through 2030)

**Recommended calibration range: $30–60B per GW in construction CapEx**, with $10–15B/GW as annual run-rate cost inclusive of operations.

### 3.4 Data Center Build Timelines

Typical: **12–24 months** from groundbreaking to operational for hyperscalers; **2–4 years** for entirely new builds. xAI's Colossus (122 days for 100K GPUs) is universally considered exceptional [107][108].

**Power is now the binding constraint.** Microsoft CFO Amy Hood: "We are, and have been, short now for many quarters" [51]. Power transformer lead times: **128 weeks (~2.5 years)** [109]. Grid connection requests: 4–7 years in key regions. RAND projects AI data centers could need **68 GW by 2027** and **327 GW by 2030** [110]. The IEA projects global data center electricity consumption doubling from ~415 TWh (2024) to ~945 TWh by 2030 [111][112].

---

## 4. Training vs. Inference Compute Allocation

### 4.1 Direct Executive Statements

**Dario Amodei** modeled the equilibrium at **~50/50 training/inference** on the Dwarkesh Patel podcast (early 2025): "Let's say half of your compute is for training and half of your compute is for inference… It's not gonna be 10%, it's not gonna be 90%" [104][113].

**Jensen Huang** (GTC 2025): "The amount of computation we have to do for inference is dramatically higher than it used to be — **100 times more, easily**." When told inference already accounted for over 40% of AI revenue, he responded: "It's about to go up **by a billion times**" [114][115][116].

**Microsoft CFO Amy Hood** (Morgan Stanley TMT Conference, 2025): "Today, when we talk about our $13 billion AI revenue number, it's **primarily inference and post-training workloads**" [117].

### 4.2 Best Available Company-Level Data

**Epoch AI's analysis of OpenAI's 2024 compute** (October 2025) — the only company-specific breakdown with primary documentation — found of ~$7B total cloud compute: **$3B to training**, **$2B to research/experimentation**, and **$1.8B to inference** [118][119]. Combined R&D (training + research) was ~71%, inference ~26%. Key finding: "The majority of OpenAI's R&D compute was likely allocated to research and experimental training runs, rather than the final training runs of released models" [120].

### 4.3 Industry-Wide Trajectory

Deloitte TMT Predictions 2026: roughly **two-thirds training / one-third inference in 2023**, reaching **parity (~50/50) in 2025**, shifting to **two-thirds inference / one-third training by 2026** [121]. VentureBeat reported: "For the first time, **inference surpassed training** in terms of total data center revenue" in late 2025 [122].

Both training and inference are growing in absolute terms — each new model generation requires 2–4× more compute — but inference is growing faster due to expanding user bases, reasoning models using 10–100× more compute per query, agentic AI creating continuous workloads, and enterprise adoption at scale.

### 4.4 Revised Estimates for the Four Archetypes

| Archetype | Paper's Current | Revised Estimate | Credible Range | Rationale |
|-----------|----------------|------------------|----------------|-----------|
| Anthropic-like | 60% training | **50–55% training** | 45–60% | Massive inference from Claude Code + enterprise API; but enormous training ambitions |
| OpenAI-like | 55% training | **55–65% training** | 50–70% | Huge ChatGPT user base drives inference; but ~71% of compute is R&D per Epoch AI |
| Google-like | 40% training | **30–40% training** | 25–45% | Serves AI to billions (Search, Maps, Gmail, YouTube). Processes 1.3 quadrillion tokens/month. Ironwood TPU designed for inference |
| xAI-like | 80% training | **70–80% training** | 65–85% | Colossus explicitly built for training. Grok 4 used RL "at pretraining scale." Inference outsourced to cloud |

The paper's existing estimates are broadly defensible. The Anthropic figure may be slightly high given explosive revenue growth; the Google figure may be slightly high given deployment scale. Key caveat: Microsoft's inference of OpenAI models (for Copilot, Azure) is excluded from OpenAI's own allocation.

---

## 5. Executive Statements on AGI Timelines and Beliefs

### 5.1 The Optimists

**Dario Amodei** (Anthropic CEO) — February 13, 2026 Dwarkesh Patel interview [123][124]: Placed **90% probability on achieving "a country of geniuses in a data center" within 10 years**, with 5% irreducible chance of major delay. Critically for the paper's methodology, he articulated the investment constraint: "If my revenue is not a trillion dollars, if it's even 800 billion, **there's no force on earth, no hedge on earth that could stop me from going bankrupt** if I buy that much compute." His October 2024 "Machines of Loving Grace" essay placed powerful AI "as early as 2026." Anthropic's March 2025 OSTP submission expected "powerful AI systems in late 2026 or early 2027."

**Sam Altman** (OpenAI CEO) — February 2025 "Three Observations" blog [125]: "We are now confident we know how to build AGI as we have traditionally understood it." Three scaling observations: intelligence scales as log of resources; cost falls ~10× per year (150× from GPT-4 to GPT-4o); socioeconomic value is "super-exponential" in intelligence. Has pivoted stated goal to superintelligence.

**Elon Musk** (xAI) — January 7, 2026 podcast [126]: "**Achieve AGI in 2026. This is not a prophecy, but an engineering calculation.**" Projected AI exceeding "the collective intelligence of all humanity" by 2030. Described 10× annual algorithmic improvement rate.

### 5.2 The Pragmatic-Economic Framing

**Sundar Pichai** (Alphabet CEO) — Q2 2024 earnings call [127]: "For Alphabet, **the risk of underinvestment in AI is far greater than the risk of overinvestment.**" Data center infrastructure "can also be used for other tasks," providing downside protection. Backed this framing with near-doubling CapEx guidance to $175–185B for 2026.

**Satya Nadella** (Microsoft CEO) — proposed an **"economic test for AGI"** based on GDP growth: "When the developed world is growing at 10%, which may have been the peak of the Industrial Revolution — that's a good benchmark for me" [117]. Dismissed "benchmark hacking" claims. Acknowledged: "There will be an overbuild" but confident "the only thing that's going to happen with all the compute build is the prices are going to come down."

**Andy Jassy** (Amazon CEO) — February 5, 2026 earnings call [53][94]: Defended $200B 2026 CapEx: "not some quixotic, top-line grab." "We have confidence that these investments will yield strong returns on invested capital." "Barbell" demand analogy: early adopters / experimenters on ends, enterprise workloads in middle.

**Mark Zuckerberg** (Meta CEO) — January 2026 [58]: Called 2026 "a big year for personal superintelligence." Guided Meta CapEx to $115–135B.

### 5.3 The Skeptics

**Yann LeCun** (Meta Chief AI Scientist → AMI Labs) — CES 2025 and December 2025 Information Bottleneck podcast: "There's absolutely no way that autoregressive LLMs will reach human intelligence." Path to superintelligence via LLMs/RL/post-training is "complete bullshit. It's just never going to work." Left Meta January 2026 to found AMI Labs, advocating JEPA and world models.

**Ilya Sutskever** (SSI / formerly OpenAI) — NeurIPS December 2024: "**Pre-training as we know it will unquestionably end… because we have but one internet.**" Compared data to fossil fuel — "peak data." Positioned as end of "age of scaling," beginning of "age of research." SSI raised $3B, valued at $32B.

**Demis Hassabis** (Google DeepMind CEO) — March 2025: "I think over the next five to 10 years" capabilities will emerge that constitute AGI. August 2025 (60 Minutes): AGI "by 2030." Proposed a "CERN for AGI" international research collaboration.

### 5.4 Inference-Time Compute Scaling

**Noam Brown** (OpenAI): "Having the bot think for just 20 seconds got the same boost in performance as **scaling up the model by 100,000× and training for 100,000 times longer.**" Identified "1 unit of test-time compute being equivalent to **1,000–10,000×** more in model size." Argued for scaling inference from ~15-minute limits to "hours, days, even longer." Framed "eight orders of magnitude" of headroom between current query costs (~$0.01) and value of solving million-dollar problems.

### 5.5 Key Mapping: Beliefs → Investment Behavior

The 2026 CapEx commitments represent the strongest "revealed belief" signal. The combined **$630B+** — in the face of no clear near-term ROI proof at this scale — implies high probability assigned to transformative AI arriving within 2–5 years. Amodei's interview is perhaps the single most useful source for the paper's methodology: he explicitly discusses how even firms highly confident in AGI must constrain spending relative to what their beliefs would justify, because the financial ruin of being "off by a couple years" on revenue timing is catastrophic.

---

## 6. Financial Parameters

### 6.1 Cost of Capital / WACC

The **10-year US Treasury yield**: ~**4.03–4.08%** as of late February 2026 (down from 4.31% January peak). Damodaran's implied **equity risk premium** (January 1, 2025): **4.33%** (S&P 500 implied return 8.91% minus 4.58% bond rate). Estimated early 2026 ERP: **4.3–4.8%**.

Damodaran January 2025 industry WACCs: Computer Software ~7.16%, Internet/Online Services ~7.6%, Semiconductors ~10.76%, market-wide average 7.63%.

**Company-specific estimates:**

| Company | Est. WACC | Cost of Equity | Credit Rating | Debt/Equity |
|---------|-----------|---------------|---------------|-------------|
| Alphabet | ~9.0–9.1% | ~9.1% (β 1.02) | Aa2/AA+ | ~9% → rising to 15–20% |
| Microsoft | ~8.5–9.5% | ~8.5–9.5% (β 1.0–1.1) | Aaa/AAA | ~25% (net cash) |
| Amazon | ~9.0–10.0% | ~9.5–10.5% (β 1.1–1.2) | A1/AA | ~50% (near-zero net debt/EBITDA) |
| Meta | ~9.5–10.5% | ~10–11% (β 1.2–1.3) | Aa3/AA- | Rising rapidly |
| NVIDIA | ~10.0–11.0% | ~10.5–11.5% (β 1.4–1.5) | High IG | ~9% |

For **private AI labs** (Anthropic, OpenAI): reasonable market beta **1.5–2.5**. Using CAPM: cost of equity = 4.05% + 2.0 × 4.33% = **~12.7% central estimate**, range **10.5–15.0%**. OpenAI's $4B revolving credit facility at SOFR + 100bps (~5.3%) is remarkably favorable for a loss-making company [30].

### 6.2 Leverage and Capital Structure

**Anthropic:** Effectively **100% equity-funded** with no reported debt instruments. Amazon's $8B initially structured as convertible notes, partly converting to equity. Latest valuation: **$380B** (February 2026) [12].

**OpenAI:** **$4B revolving credit facility** (October 2024, JPMorgan-led, largely undrawn) [30]. Partners have accumulated ~$100B in borrowings tied to OpenAI (SoftBank, Oracle, CoreWeave) [128]. Cash: ~$64B (late 2025). Latest valuation: **$500B** (October 2025), potentially $730–830B.

**xAI:** **$5B+ in direct debt** (Morgan Stanley-arranged secured notes and term loans, July 2025) plus ~$20B SPV for GPU purchases (Apollo, Diameter Capital). X Corp. carries ~$12B in legacy acquisition debt [44][48].

**Google/Alphabet:** Long-term debt ~$12.3B at end of 2025 (low leverage). However, bond issuance surging: $57B+ in bonds including a 100-year sterling-denominated bond at 120bps over gilts [129].

### 6.3 Cost of Debt and Industry Debt Trends

The sector is undergoing a historic capital structure transformation. Hyperscalers issued **$121B in bonds in 2025** — 4× the five-year average of $28B — with another $45B in the first two months of 2026. Morgan Stanley expects hyperscalers to borrow **$400B in 2026** [98]. Notable issuances: Alphabet $57B+, Meta $30B (fifth-largest IG bond deal ever), Oracle $61.5B total (2022–2025). A nascent data center ABS market has produced $20B in deals since early 2024.

Credit spreads remain tight: <100bps for Alphabet/Microsoft, 80–110bps for Meta/Amazon, 125–139bps for Oracle.

---

## 7. Scaling Laws and Diminishing Returns

### 7.1 Pre-Training Scaling

The consensus is that pre-training scaling yields logarithmic returns. The power law relationship means lowering test loss by 2× requires roughly **1,000,000× more compute** at current exponents (loss ∝ Compute^−0.05 to −0.07). Sutskever's NeurIPS 2024 declaration reflects the data constraint.

However, **two new scaling dimensions have emerged**: (1) RL post-training — Amodei confirmed "the same scaling in RL that we saw for pre-training" [113] — and (2) inference-time compute (Brown's 20-second thinking = 100,000× more training data). An important nuance from arXiv:2509.09677 ("Illusion of Diminishing Returns," 2025): for long-horizon agentic tasks, scaling shows "non-diminishing improvements in the number of turns it can execute."

### 7.2 DeepSeek Efficiency

DeepSeek V3 (671B parameters, MoE with 37B activated/token) pre-trained on 14.8T tokens using 2,664K H800 GPU hours at ~**$5.6M for the final training run** — roughly 10× lower compute than comparable models [62][63]. R1's RL cost: ~$294,000. API pricing ~$0.55/$2.19 per million tokens — **20–50× cheaper** than OpenAI o1.

The January 27, 2025 market reaction (NVIDIA -$600B in one day) was dramatic but short-lived: hyperscalers reaffirmed CapEx within weeks. The Jevons Paradox narrative (lower costs → more demand) became dominant.

### 7.3 Operating Costs

**Power**: Average US commercial electricity $0.082/kWh; hyperscaler PPA rates $0.03–0.06/kWh. Wholesale near data center hotspots has risen **up to 267%** since 2020 [130][131].

**PUE**: Google fleet-wide 1.09; hyperscale average 1.10–1.20 [131].

**Annual operating costs**: ~**30–40% of hardware CapEx** (for 8-GPU H100 at ~$300K, ~$100K/year operating).

**Blackwell generation**: ~4× training speedup and 30× inference speedup vs. H100 at ~2× per-unit price, requiring liquid cooling.

---

## 8. Industry Structure and Competition

### 8.1 The Sequoia "$600B Question" — Updated

David Cahn (Sequoia, summer 2025 update): required revenue recalculated at **~$840B** (up from ~$500B). "I do think we're in an AI bubble. You can see the fragility" [132]. Goldman Sachs (late 2025): maintaining returns would require **$1 trillion in annual AI profits** [133]. Barclays: equivalent of **12,000 ChatGPT-sized products** needed to justify current CapEx.

Counter-narrative: OpenAI tripled to ~$13B; Anthropic grew from $1B to $14B ARR in 14 months; AWS AI crossed $10B ARR; Google Cloud hit $70B run rate with expanding margins. Foundation Capital / Goldman economist (Joseph Briggs): generative AI could boost US productivity 9%, GDP 6.1% over a decade.

### 8.2 Market Structure

Goldman Sachs assessed "there's not going to be more than four" firms that can ultimately compete at the frontier. Open-source models (Llama, DeepSeek, Mistral) now fall within a **7.5% performance gap** of proprietary frontier models on MMLU. Character.AI abandoned LLM development because "it got insanely expensive."

### 8.3 Strategic Dynamics and Preemption

Sequoia Capital's "Game Theory of AI CapEx" analysis (December 2024): companies "felt they had no choice but to spend aggressively to ensure their continued dominance. If they didn't spend, others would." DeepSeek R1's efficiency breakthrough caused **no firm to reduce investment** — instead, the Jevons Paradox narrative justified continued or increased spending.

---

## 9. Additional Data Points

### 9.1 Financial Distress Cases

**Stability AI:** <$5M quarterly revenue against >$30M quarterly losses (Q1 2024), burning ~$8M/month with ~$100M owed to creditors. CEO Emad Mostaque resigned March 2024. Survived through recapitalization with >$100M in debt forgiveness.

**Inflection AI:** Microsoft hired co-founders Mustafa Suleyman and Karén Simonyan plus ~70 staff (March 2024), paying **$650M** ($620M model license + $30M hiring waiver).

**Character.AI:** Google deal ($2.7B, August 2024) with co-founders and 30 researchers hired. DOJ examining whether deal functioned as de facto merger.

### 9.2 Time-to-Build

Typical: **12–24 months** (hyperscaler with established teams); **2–4 years** (entirely new builds). xAI Colossus: **122 days** for 100K GPUs — Jensen Huang: "only one person in the world who could do that" and "projects of this scale typically take around four years" [107]. Key constraints: power transformers (128-week lead times), grid connections (4–7 years), GPU supply (easing but Blackwell allocation competitive).

### 9.3 Regulatory and Policy

**US GPU export controls:** Biden's January 2025 "AI Diffusion Rule" (three-tier country system, ~50K GPU cap for Tier 2) was **rescinded by the Trump administration in May 2025**; replacement pending. August 2025: novel policy requiring NVIDIA to pay 15% of China H20 sales to USG.

**CHIPS Act:** >$32B of $39B fab construction earmark allocated, catalyzing >$450–640B in private investment across 140+ projects. Trump administration rescinded $7.4B in R&D funds (August 2025).

**Power and zoning:** Data centers consumed 26% of Virginia's electricity (2023). PJM capacity market impacts raised residential bills $16–18/month. July 2025 Executive Order accelerated federal permitting for data center infrastructure.

---

## Summary Calibration Table (Early 2026)

| Parameter | Anthropic-like | OpenAI-like | Google-like | xAI-like |
|-----------|---------------|-------------|-------------|----------|
| 2025 Revenue | ~$4–5B collected; $9B ARR EOY | ~$12–13B collected; $20B ARR EOY | ~$59–60B (Cloud segment) | ~$200M+ standalone; ~$3.8B consolidated |
| 2026 Revenue Target | $20–26B ARR | ~$29–30B | $70B+ Cloud run rate | ~$1B (management) |
| Latest Valuation | $380B (Feb 2026) | $500B–$830B | ~$2.3T market cap | $250B (post-SpaceX) |
| 2025 CapEx/Infra | ~$3B cloud spend + fundraising | ~$12B+ Azure spend | $91.4B (total Alphabet) | ~$10B+ est. |
| 2026 CapEx Guidance | $80B+ cloud commitments (multi-year) | $500B Stargate (4-year) | $175–185B | Colossus 2: ~$18–20B |
| GPU Fleet (H100-equiv.) | 800K–2M (cloud) | 1M–1.5M | 2M–3M (mostly TPU) | 200K–555K (owned) |
| Training % of Compute | 50–55% | 55–65% | 30–40% | 70–80% |
| Burn Rate | ~$3B/yr (2025) | ~$8.5B/yr (2025) | Profitable ($73B FCF) | ~$12B/yr |
| Break-Even Target | 2028 | 2029–2030 | Already profitable | 2027 (management) |
| Debt/Capital | ~0% | <5% direct | ~15–20% (rising) | ~10–15% |
| Est. Cost of Equity | 10.5–15% | 10.5–15% | ~9.1% | 12–18% (high uncertainty) |
| AGI Timeline (CEO) | "90% within 10 years" | "Confident we know how to build AGI" | "5–10 years" (Hassabis) | "AGI in 2026" (Musk) |

---

## References

[1] Introl Blog, "Hyperscaler CapEx Hits $690B in 2026," February 2026. https://introl.com/blog/hyperscaler-capex-690-billion-microsoft-azure-power-bottleneck-2026

[2] Futurum Group, "AI Capex 2026: The $690B Infrastructure Sprint," February 2026. https://futurumgroup.com/insights/ai-capex-2026-the-690b-infrastructure-sprint/

[3] SaaStr, "Anthropic Just Hit $14 Billion in ARR. Up From $1 Billion Just 14 Months Ago," February 2026. https://www.saastr.com/anthropic-just-hit-14-billion-in-arr-up-from-1-billion-just-14-months-ago/

[4] PYMNTS, "OpenAI's Annual Recurring Revenue Tripled to $20 Billion in 2025," January 2026. https://www.pymnts.com/artificial-intelligence-2/2026/openais-annual-recurring-revenue-tripled-to-20-billion-in-2025/

[5] CNBC, "Anthropic fundraising: Round wraps above $10 billion and could rise," January 27, 2026. https://www.cnbc.com/2026/01/27/anthropic-fundraising-microsoft-nvidia.html

[6] Sacra, "Anthropic revenue, valuation & funding," 2026. https://sacra.com/c/anthropic/

[7] Substack (Shanaka Anslem Perera), "The Growth Miracle and the Six Fractures: Anthropic at $380 Billion," 2026. https://shanakaanslemperera.substack.com/p/the-growth-miracle-and-the-six-fractures

[8] TechCrunch, "Anthropic projects $70B in revenue by 2028: Report," November 4, 2025. https://techcrunch.com/2025/11/04/anthropic-expects-b2b-demand-to-boost-revenue-to-70b-in-2028-report/

[9] TSG Invest, "Anthropic Stock: Private Investment Guide," 2026. https://tsginvest.com/anthropic-pbc/

[10] Acquinox Capital, "Anthropic: Investor insights," 2026. https://acquinox.capital/blog/anthropic-investor-insights

[11] Private Equity Insights, "Investors pile into Anthropic as revenues top $9bn run rate," 2025. https://pe-insights.com/investors-pile-into-anthropic-as-revenues-top-9bn-run-rate/

[12] Anthropic, "Anthropic raises $30 billion Series G funding, $380 billion post-money valuation," February 12, 2026. https://www.anthropic.com/news/anthropic-raises-30-billion-series-g-funding-380-billion-post-money-valuation

[13] CNBC, "Anthropic closes $30 billion funding round at $380 billion valuation," February 12, 2026. https://www.cnbc.com/2026/02/12/anthropic-closes-30-billion-funding-round-at-380-billion-valuation.html

[14] Texau, "How Much Did Anthropic Raise? Funding & Key Investors," 2026. https://www.texau.com/profiles/anthropic

[15] Crunchbase News, "Anthropic Raises $30B At $380B Valuation," February 2026. https://news.crunchbase.com/ai/anthropic-raises-30b-second-largest-deal-all-time/

[16] Yahoo Finance, "OpenAI CFO says annualized revenue crosses $20 billion in 2025," January 2026. https://finance.yahoo.com/news/openai-cfo-says-annualized-revenue-173519097.html

[17] SaaStr, "OpenAI Crosses $12 Billion ARR," 2025. https://www.saastr.com/openai-crosses-12-billion-arr-the-3-year-sprint-that-redefined-whats-possible-in-scaling-software/

[18] PM Insights, "Anthropic Approaches $7B Run Rate in 2025, Outpaces OpenAI," 2025. https://www.pminsights.com/insights/anthropic-approaches-7b-run-rate-in-2025-outpaces-openai

[19] CNBC, "OpenAI resets spending expectations, targets around $600 billion by 2030," February 20, 2026. https://www.cnbc.com/2026/02/20/openai-resets-spend-expectations-targets-around-600-billion-by-2030.html

[20] Fortune, "OpenAI forecasts its revenue will top $280 billion in 2030," February 20, 2026. https://fortune.com/2026/02/20/openai-revenue-forecast-280-billion-2030-capex-sam-altman/

[21] LessWrong, "OpenAI lost $5 billion in 2024 (and its losses are increasing)," 2025. https://www.lesswrong.com/posts/CCQsQnCMWhJcCFY9x/openai-lost-usd5-billion-in-2024-and-its-losses-are

[22] The Economy, "OpenAI Posts Huge Losses Despite Soaring Sales," October 28, 2025. https://economy.ac/news/2025/10/202510280999

[23] The Information, "OpenAI's First Half Results: $4.3 Billion in Sales, $2.5 Billion Cash Burn," 2025. https://www.theinformation.com/articles/openais-first-half-results-4-3-billion-sales-2-5-billion-cash-burn

[24] R&D World, "Facing $14B losses in 2026, OpenAI is now seeking $100B in funding," February 2026. https://www.rdworldonline.com/facing-14b-losses-in-2026-openai-is-now-seeking-100b-in-funding-but-can-it-ever-turn-a-profit/

[25] sanj.dev, "The Real Cost of AI: Inside OpenAI's $13.5B Burn Rate," 2025. https://sanj.dev/post/real-cost-of-ai-openai-financials

[26] Fortune, "OpenAI says it plans to report stunning annual losses through 2028," November 12, 2025. https://fortune.com/2025/11/12/openai-cash-burn-rate-annual-losses-2028-profitable-2030-financial-documents/

[27] Fortune, "OpenAI completes for-profit restructuring and grants Microsoft a 27% stake," October 28, 2025. https://fortune.com/2025/10/28/openai-for-profit-restructuring-microsoft-stake/

[28] CNBC, "OpenAI completes restructure, solidifying Microsoft as a major shareholder," October 28, 2025. https://www.cnbc.com/2025/10/28/open-ai-for-profit-microsoft.html

[29] Sacra, "OpenAI revenue, valuation & funding," 2026. https://sacra.com/c/openai/

[30] CNBC, "OpenAI gets $4 billion revolving credit line on top of latest funding," October 3, 2024. https://www.cnbc.com/2024/10/03/openai-gets-4-billion-revolving-credit-line-on-top-of-latest-funding.html

[31] PYMNTS, "Report: Half of OpenAI's Pending $40 Billion Funding Round Depends on Restructuring," 2025. https://www.pymnts.com/artificial-intelligence-2/2025/report-half-of-openais-pending-40-billion-funding-round-depends-on-restructuring

[32] Epoch AI, "OpenAI is projecting unprecedented revenue growth," 2026. https://epoch.ai/gradient-updates/openai-is-projecting-unprecedented-revenue-growth

[33] 9to5Google, "Alphabet reports Q4 2025 revenue of $113.8 billion," February 4, 2026. https://9to5google.com/2026/02/04/alphabet-q4-2025-earnings/

[34] SEC.gov, "Alphabet Announces Fourth Quarter and Fiscal Year 2025 Results," February 4, 2026. https://www.sec.gov/Archives/edgar/data/1652044/000165204426000012/googexhibit991q42025.htm

[35] Google Blog, "Alphabet earnings, Q4 2025: CEO's remarks," February 4, 2026. https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q4-2025/

[36] AlphaSense, "Alphabet Inc Earnings - Analysis & Highlights for Q4 2025," 2026. https://www.alpha-sense.com/earnings/goog/

[37] Alphabet Q4 2025 earnings call transcript (via AlphaSense and SEC filing).

[38] Bloomberg, "Musk's xAI Burns Almost $8 Billion, Reveals Optimus Plan," January 9, 2026. https://www.bloomberg.com/news/articles/2026-01-09/musk-s-xai-reports-higher-quarterly-loss-plans-to-power-optimus

[39] Yahoo Finance, "Musk's xAI quarterly net loss widens to $1.46 billion," January 2026. https://finance.yahoo.com/news/musks-xai-posts-net-quarterly-003131361.html

[40] Summit Ventures Partners, "xAI," 2026. https://www.summit-ventures.net/company/xai/

[41] Yahoo Finance, "Elon Musk's xAI Eyes $14 Billion Revenue, $13 Billion EBITDA by 2029," 2025. https://finance.yahoo.com/news/elon-musks-xai-eyes-14-165033326.html

[42] Wikipedia, "xAI (company)," February 2026. https://en.wikipedia.org/wiki/XAI_(company)

[43] Futurum Group, "SpaceX Acquires xAI: Rockets, Starlink, and AI Under One Roof," February 2026. https://futurumgroup.com/insights/spacex-acquires-xai-rockets-starlink-and-ai-under-one-roof/

[44] The Irish Times, "Musk's xAI reports $1.46bn quarterly loss," January 9, 2026. https://www.irishtimes.com/business/2026/01/09/musks-xai-reports-146bn-quarterly-loss/

[45] Sullivan & Cromwell, "S&C Advises xAI in Acquisition by SpaceX in Historic $250 Billion Deal," February 2026. https://www.sullcrom.com/About/Rankings/2026/February/SC-Advises-xAI-Acquisition-SpaceX-Historic-250-Billion-Deal

[46] CNBC, "Musk's xAI, SpaceX combo is the biggest merger of all time, valued at $1.25 trillion," February 3, 2026. https://www.cnbc.com/2026/02/03/musk-xai-spacex-biggest-merger-ever.html

[47] Sacra, "xAI revenue, valuation & funding," 2026. https://sacra.com/c/xai/

[48] The Hollywood Reporter, "Elon Musk's xAI Raises $20 Billion in New Funding Round," 2025. https://www.hollywoodreporter.com/business/digital/elon-musk-xai-raises-20-billion-new-funding-round-1236465907/

[49] CNBC, "Elon Musk's xAI raises $20 billion from investors including Nvidia, Cisco, Fidelity," January 6, 2026. https://www.cnbc.com/2026/01/06/elon-musk-xai-raises-20-billion-from-nvidia-cisco-investors.html

[50] Tech Funding News, "xAI nears $230B valuation in $20B Nvidia-led raise," January 2026. https://techfundingnews.com/xai-nears-a-230b-valuation-with-20b-funding-from-nvidia-and-others-to-challenge-openai-and-anthropic/

[51] Fintool, "Microsoft Beats on Revenue and EPS, But Record $37.5B Capex Spooks Investors," January 2026. https://fintool.com/news/microsoft-q2-record-capex-cloud-ai

[52] AlphaSense, "Microsoft Corp Earnings - Analysis & Highlights for Q4 2025," 2026. https://www.alpha-sense.com/earnings/msft/

[53] Futurum Group, "Amazon Q4 FY 2025: Revenue Beat, AWS +24% Amid $200B Capex Plan," February 2026. https://futurumgroup.com/insights/amazon-q4-fy-2025-revenue-beat-aws-24-amid-200b-capex-plan/

[54] Next Platform, "The Twin Engine Strategy That Propels AWS Is Working Well," February 8, 2026. https://www.nextplatform.com/2026/02/08/the-twin-engine-strategy-that-propels-aws-is-working-well/

[55] NVIDIA Newsroom, "NVIDIA Announces Financial Results for Third Quarter Fiscal 2026," November 19, 2025. https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2026

[56] Beancount, "NVIDIA Q3 FY2026 Earnings: Inside the $57B Quarter," February 2026. https://beancount.io/blog/2026/02/09/nvidia-q3-fy2026-earnings-analysis

[57] Bullfincher, "NVIDIA Corporation Revenue Breakdown By Segment," 2026. https://bullfincher.io/companies/nvidia-corporation/revenue-by-segment

[58] Meta Investor Relations, "Meta Reports Fourth Quarter and Full Year 2025 Results," January 2026. https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Fourth-Quarter-and-Full-Year-2025-Results/default.aspx

[59] YourStory, "Mark Zuckerberg says 2026 will be a 'big year' for personal superintelligence as Meta boosts capex," January 2026. https://yourstory.com/2026/01/mark-zuckerberg-2026-big-year-personal-superintelligence-meta-capex

[60] MLQ, "Mistral AI surges revenue 20-fold to over $400 million ARR," 2025. https://mlq.ai/news/mistral-ai-surges-revenue-20-fold-to-over-400-million-arr-amid-europes-ai-push/

[61] Wikipedia, "Cohere," 2026. https://en.wikipedia.org/wiki/Cohere

[62] Electro IQ, "DeepSeek AI Statistics By Users, Usage, Funding and Facts," 2025. https://electroiq.com/stats/deepseek-ai-statistics/

[63] Wikipedia, "DeepSeek," 2026. https://en.wikipedia.org/wiki/DeepSeek

[64] Data Center Dynamics, "Anthropic cloud spend expected to reach $80bn through 2029," 2025. https://www.datacenterdynamics.com/en/news/anthropic-cloud-spend-expected-to-reach-80bn-through-2029/

[65] Phemex, "Anthropic Projects $80 Billion Cloud Spend by 2029," 2025. https://phemex.com/news/article/anthropic-projects-80-billion-cloud-spend-with-amazon-google-microsoft-61151

[66] Where's Your Ed At, "This Is How Much Anthropic and Cursor Spend On Amazon Web Services," November 2025. https://www.wheresyoured.at/costs/

[67] CNBC, "Google and Anthropic announce cloud deal worth tens of billions of dollars," October 23, 2025. https://www.cnbc.com/2025/10/23/anthropic-google-cloud-deal-tpu.html

[68] Investing.com, "Google's Massive Anthropic Cloud Deal: The Hidden Winner in the AI Gold Rush," 2025. https://www.investing.com/analysis/googles-massive-anthropic-cloud-deal-the-hidden-winner-in-the-ai-gold-rush-200668877

[69] TechCrunch, "Anthropic announces $50 billion data center plan," November 12, 2025. https://techcrunch.com/2025/11/12/anthropic-announces-50-billion-data-center-plan/

[70] Anthropic, "Anthropic invests $50 billion in American AI infrastructure," November 2025. https://www.anthropic.com/news/anthropic-invests-50-billion-in-american-ai-infrastructure

[71] Tomasz Tunguz, "OpenAI's $1 Trillion Infrastructure Spend," 2026. https://tomtunguz.com/openai-hardware-spending-2025-2035

[72] Yahoo Finance, "Leaked documents shed light into how much OpenAI pays Microsoft," 2025. https://finance.yahoo.com/news/leaked-documents-shed-light-much-004741535.html

[73] OpenAI, "Announcing The Stargate Project," January 21, 2025. https://openai.com/index/announcing-the-stargate-project/

[74] Data Center Dynamics, "Building Stargate: Talking to OpenAI about its trillion-dollar data center vision," 2025. https://www.datacenterdynamics.com/en/analysis/openai-building-stargate-nvidia-oracle-chatgpt/

[75] OpenAI, "OpenAI, Oracle, and SoftBank expand Stargate with five new AI data center sites," September 2025. https://openai.com/index/five-new-stargate-sites/

[76] Q4cdn / Alphabet, "Alphabet Announces Fourth Quarter and Fiscal Year 2025 Results" (PDF). https://s206.q4cdn.com/479360582/files/doc_financials/2025/q4/2025q4-alphabet-earnings-release.pdf

[77] CNBC, "Google's $85 billion capital spend spurred by cloud, AI demand," July 23, 2025. https://www.cnbc.com/2025/07/23/googles-85-billion-capital-spend-spurred-by-cloud-ai-demand.html

[78] CNBC, "Google expects 'significant increase' in capital expenditure in 2026," October 29, 2025. https://www.cnbc.com/2025/10/29/google-expects-significant-increase-in-capex-in-2026-execs-say.html

[79] CNBC, "Alphabet expects to invest about $75 billion in capital expenditures in 2025," February 4, 2025. https://www.cnbc.com/2025/02/04/alphabet-expects-to-invest-about-75-billion-in-capex-in-2025.html

[80] Global Data Center Hub, "Google Q3 2025: $93 Billion CapEx Marks the Moment AI Became Infrastructure," 2025. https://www.globaldatacenterhub.com/p/google-q3-2025-93-billion-capex-marks

[81] Google Blog, "Ironwood: The first Google TPU for the age of inference," 2025. https://blog.google/products/google-cloud/ironwood-tpu-age-of-inference/

[82] Fortune, "Alphabet is confident about plans to double capex spending to a possible $185 billion," February 4, 2026. https://fortune.com/2026/02/04/alphabet-google-ai-spending-supply-constraints/

[83] xAI, "Colossus: The World's Largest AI Supercomputer." https://x.ai/colossus

[84] R&D World, "How xAI turned a factory shell into an AI 'Colossus' for Grok 3," 2025. https://www.rdworldonline.com/how-xai-turned-a-factory-shell-into-an-ai-colossus-to-power-grok-3-and-beyond/

[85] HPCwire, "Colossus AI Hits 200,000 GPUs as Musk Ramps Up AI Ambitions," May 13, 2025. https://www.hpcwire.com/2025/05/13/colossus-ai-hits-200000-gpus-as-musk-ramps-up-ai-ambitions/

[86] FinancialContent, "The Compute Crown: xAI Scales 'Colossus' to 200,000 GPUs," December 25, 2025. https://markets.financialcontent.com/stocks/article/tokenring-2025-12-25-the-compute-crown-xai-scales-colossus-to-200000-gpus-following-massive-funding-surge

[87] Introl Blog, "xAI Colossus Hits 2 GW: 555,000 GPUs, $18B, Largest AI Site," January 2026. https://introl.com/blog/xai-colossus-2-gigawatt-expansion-555k-gpus-january-2026

[88] MLQ, "xAI Seeks $12 Billion Funding for Colossus 2 Supercluster," 2025. https://mlq.ai/news/xai-seeks-12-billion-funding-for-colossus-2-supercluster-unveils-deployment-timeline/

[89] Fintool, "Musk's xAI Buys Third Building, Eyes 2 Gigawatts and 1 Million GPUs," December 2025. https://fintool.com/news/xai-colossus-third-building-2gw-expansion

[90] NextBigFuture, "Construction, Power Timeline for xAI to Reach a 3 Million GPU Supercluster," March 2025. https://www.nextbigfuture.com/2025/03/construction-power-timeline-for-xai-to-reach-a-3-million-gpu-supercluster.html

[91] Interesting Engineering, "xAI launches world-first gigawatt-scale AI training cluster for Grok," 2025. https://interestingengineering.com/ai-robotics/elon-musk-xai-gigawatt-scale-ai-training-cluster

[92] The Information, "Musk's xAI Burned Through $7.8 Billion in Cash in First Nine Months of 2025," 2025. https://www.theinformation.com/briefings/musks-xai-burned-7-8-billion-cash-first-nine-months-2025

[93] 24/7 Wall St., "Amazon's $200 Billion AI Spending Shocker Has Wall Street Asking One Question," February 24, 2026. https://247wallst.com/investing/2026/02/24/amazons-200-billion-ai-spending-shocker-has-wall-street-asking-one-question/

[94] Cloud Wars, "Amazon Sets World Record for CapEx Spending, and CEO Andy Jassy Is Delighted," February 2026. https://cloudwars.com/innovation-leadership/amazon-sets-world-record-for-capex-spending-and-ceo-andy-jassy-is-delighted/

[95] Data Center Dynamics, "Meta plans 'notably larger' capex spend on AI data centers in 2026," January 2026. https://www.datacenterdynamics.com/en/news/meta-plans-notably-larger-capex-spend-on-ai-data-centers-in-2026-compute-expectations-already-higher-than-last-quarter-prediction/

[96] Introl Blog, "Hyperscaler CapEx Hits $600B in 2026," January 2026. https://introl.com/blog/hyperscaler-capex-600b-2026-ai-infrastructure-debt-january-2026

[97] IEEE ComSoc Technology Blog, "AI spending boom accelerates: Big tech to invest an aggregate of $400 billion in 2025; much more in 2026!" November 1, 2025. https://techblog.comsoc.org/2025/11/01/ai-spending-boom-accelerates-big-tech-to-invest-invest-an-aggregate-of-400-billion-in-2025-more-in-2026/

[98] Morgan Stanley and JP Morgan estimates (multiple press reports, 2025–2026).

[99] LessWrong, "Estimates of GPU or equivalent resources of large AI players," November 28, 2024. https://www.lesswrong.com/posts/bdQhzQsHjNrQp7cNS/estimates-of-gpu-or-equivalent-resources-of-large-ai-players

[100] LessWrong (CharlesD post, fetched content), November 2024.

[101] ACM Communications, "The Race to 100 Million GPUs," 2025. https://cacm.acm.org/news/the-race-to-100-million-gpus/

[102] IntuitionLabs, "NVIDIA AI GPU Prices: H100 ($27K-$40K) & H200 ($315K/8-GPU) Cost Guide," 2025. https://intuitionlabs.ai/articles/nvidia-ai-gpu-pricing-guide

[103] byteiota, "AI Inference Costs 2026: The Hidden 15-20x GPU Crisis," 2026. https://byteiota.com/ai-inference-costs-2026-the-hidden-15-20x-gpu-crisis/

[104] Dwarkesh Podcast, "Dario Amodei — 'We are near the end of the exponential,'" February 2026. https://www.dwarkesh.com/p/dario-amodei-2

[105] Investing.com, "How much does a GW of data center capacity actually cost?" 2025. https://www.investing.com/news/stock-market-news/how-much-does-a-gw-of-data-center-capacity-actually-cost-4314046

[106] Next Platform, "The Twin Engine Strategy That Propels AWS Is Working Well," February 8, 2026. https://www.nextplatform.com/2026/02/08/the-twin-engine-strategy-that-propels-aws-is-working-well/

[107] Introl Blog, "xAI's Memphis Colossus: Anatomy of a 100,000 GPU Supercomputer," 2024. https://introl.com/blog/xai-memphis-colossus-100000-gpu-supercomputer-infrastructure

[108] Introl Blog, "Anthropic's $50 Billion Data Center Plan," December 2025. https://introl.com/blog/anthropic-50-billion-data-center-plan-december-2025

[109] Deloitte TMT Predictions 2026 (cited in multiple press reports).

[110] RAND, "AI's Power Requirements Under Exponential Growth," 2025. https://www.rand.org/pubs/research_reports/RRA3572-1.html

[111] IEA, "Energy demand from AI — Energy and AI — Analysis," 2025. https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai

[112] Multiple sources on data center energy: SolarTech, Socomec, Seeking Alpha.

[113] The Singju Post, "Anthropic CEO Dario Amodei's Interview on Dwarkesh Podcast (Transcript)," 2026. https://singjupost.com/anthropic-ceo-dario-amodeis-interview-on-dwarkesh-podcast-transcript/

[114] HPCwire, "Nvidia Preps for 100x Surge in Inference Workloads, Thanks to Reasoning AI Agents," March 19, 2025. https://www.hpcwire.com/bigdatawire/2025/03/19/nvidia-preps-for-surge-in-inference-workloads-thanks-to-reasoning-ai-agents/

[115] PIAX Insights, "Nvidia's Future Vision: Jensen Huang's GTC 2025 Keynote Highlights," 2025. https://blog.piax.org/nvidias-future-vision-jensen-huangs-gtc-2025-keynote-highlights/

[116] Entrepreneur, "Nvidia CEO Jensen Huang Says the New ChatGPT Needs '100 Times More' of His Company's AI Chips," 2025. https://www.entrepreneur.com/business-news/nvidia-ceo-says-reasoning-ai-needs-100-times-more-ai-chips/487699

[117] Microsoft, "Morgan Stanley TMT Conference," 2025. https://www.microsoft.com/en-us/investor/events/fy-2025/morgan-stanley-tmt-conference

[118] Epoch AI, "Most of OpenAI's 2024 compute went to experiments," October 2025. https://epoch.ai/data-insights/openai-compute-spend

[119] Epoch AI (fetched content from [118]).

[120] Epoch AI analysis detailed breakdown (from [118]).

[121] Deloitte TMT Predictions 2026 (cited in multiple sources).

[122] VentureBeat, "Nvidia just admitted the general-purpose GPU era is ending," 2025/2026. https://venturebeat.com/infrastructure/inference-is-splitting-in-two-nvidias-usd20b-groq-bet-explains-its-next-act

[123] Dwarkesh Podcast, "Dario Amodei — 'We are near the end of the exponential,'" February 13, 2026. https://www.dwarkesh.com/p/dario-amodei-2

[124] Transcript of Amodei interview (from [113]).

[125] Sam Altman, "Three Observations," OpenAI blog, February 2025.

[126] Elon Musk, January 7, 2026 podcast with Peter Diamandis (multiple press reports).

[127] Futu News, "Google's phone call has four main points: the risk of AI 'underinvestment' is much greater than the risk of 'overinvestment,'" 2024. https://news.futunn.com/en/post/45379276/google-s-phone-call-has-four-main-points-the-risk

[128] Fortune, "OpenAI's partners are carrying $96 billion in debt," November 28, 2025. https://fortune.com/2025/11/28/openai-partners-96-billion-debt/

[129] Yahoo Finance, "Alphabet Embarks on Global Bond Spree to Fund Record Spending," 2026. https://finance.yahoo.com/news/alphabet-looks-raise-15-billion-133028283.html

[130] TechSpot, "Sam Altman compares AI energy use to the cost of 'training' humans," 2025. https://www.techspot.com/news/111431-sam-altman-compares-ai-energy-use-cost-training.html

[131] Multiple sources on power costs and PUE: IEA [111], SolarTech, Socomec.

[132] Preben Ormen, "The AI Investment Reality Check: A $600B Revenue Gap," 2025. https://prebenormen.com/artificial-intelligence/economics/the-ai-investment-reality-check-a-600b-revenue-gap

[133] Goldman Sachs estimates (cited in multiple press reports, late 2025 / early 2026).

---

*Document compiled February 24, 2026. All figures represent best available public estimates. For private companies, press reports citing "people familiar with the matter" are noted. Where estimates vary widely, ranges are provided. Calibration is intentionally stylized — order-of-magnitude accuracy is sufficient for the paper's real options framework.*
