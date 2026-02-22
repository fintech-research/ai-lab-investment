# The Trillion-Dollar Bet on Intelligence
## AI Infrastructure Spending, Compute Allocation, and AGI Timelines (2024–2026)

---

The world's most powerful technology executives are wagering unprecedented sums — approaching **$700 billion in combined 2026 capital expenditure** from just four companies — that artificial intelligence will prove to be the most consequential technology since electricity. Their reasoning, timelines, and strategic disagreements reveal an industry caught between genuine conviction and competitive compulsion, where the stated logic is remarkably uniform ("the risk of underinvesting is dramatically greater than the risk of overinvesting," as Sundar Pichai put it in July 2024) but the underlying assumptions diverge sharply. What began as a straightforward bet on scaling pre-training compute has fractured into a multi-front debate about inference-time reasoning, algorithmic efficiency, and whether current architectures can reach human-level intelligence at all.

---

## "You should expect OpenAI to spend trillions"

The scale of announced AI infrastructure investment between January 2024 and early 2026 has no precedent in corporate history. The trajectory tells the story: Amazon, Alphabet, Meta, and Microsoft spent roughly **$220–225 billion** on capital expenditure in 2024, accelerated to approximately **$375 billion** in 2025, and guided toward **$660–690 billion** for 2026. Amazon alone projected **$200 billion in 2026 capex** — announced on its February 2026 earnings call as the single largest one-year corporate capital expenditure ever, prompting an immediate 11% stock decline. [[1]](#ref1) [[2]](#ref2)

The reasoning executives offer follows a consistent pattern: demand outstrips supply, the technology is improving predictably, and falling behind would be competitively fatal. Google CFO Anat Ashkenazi stated on the Q4 2024 call that "we exited the year with more demand than we had available capacity." [[3]](#ref3) AWS CEO Matt Garman echoed: "Even with all of this investment, my best estimation is we will be capacity constrained for the next couple of years." Meta CFO Susan Li noted in January 2026 that "demands for compute resources across the company have increased even faster than our supply." [[4]](#ref4) [[5]](#ref5)

Sam Altman has been the most explicit about the philosophical framework. In his February 2025 blog post "Three Observations," he articulated a three-part thesis: intelligence equals the logarithm of resources applied, the cost per unit of AI capability falls **roughly 10x every 12 months** (which he noted is "unbelievably stronger" than Moore's Law at 2x every 18 months), and the socioeconomic value of linearly increasing intelligence is "super-exponential." [[6]](#ref6) By August 2025, Altman told Bloomberg: "You should expect OpenAI to spend trillions of dollars on data center construction in the not very distant future." [[7]](#ref7)

The **Stargate project**, announced January 21, 2025 at the White House alongside President Trump, crystallized the ambition: a **$500 billion** commitment over four years from SoftBank, OpenAI, Oracle, and Abu Dhabi's MGX, with $100 billion deployed immediately. [[8]](#ref8) By September 2025, the project had expanded to seven U.S. sites spanning over 7 GW of planned capacity. [[9]](#ref9) OpenAI separately committed approximately **$1.4 trillion** in infrastructure across seven major vendors over eight years. By October 2025, Altman stated OpenAI wanted to reach **$1 trillion per year** in infrastructure spend. [[10]](#ref10)

Anthropic's approach to capital allocation offers the starkest articulation of the risk calculus. Dario Amodei, speaking on the Dwarkesh Patel podcast in February 2026, described what he called the "cone of uncertainty": "I could buy $1 trillion of compute that starts at the end of 2027. If my revenue is not $1 trillion dollars, if it's even $800 billion, there's no force on Earth, there's no hedge on Earth that could stop me from going bankrupt." [[11]](#ref11) Anthropic itself raised over **$57 billion** in total funding through its February 2026 Series G round at a **$380 billion valuation**, with revenue growing tenfold for three consecutive years — from zero to $100 million in 2023, to $1 billion in 2024, to approximately $10 billion in 2025. [[12]](#ref12)

**Summary of 2026 capex commitments:**

| Company | 2026 Capex Guidance |
|---|---|
| Amazon (AWS) | ~$200B |
| Alphabet (Google) | ~$75–185B |
| Meta | ~$60–65B |
| Microsoft | ~$80B |
| **Total (approx.)** | **~$660–690B** |

---

## The Inference Revolution Rewrites the Compute Calculus

Perhaps the most consequential technical shift in this period was the emergence of **inference-time compute scaling** — the discovery that spending more computation when a model *answers* a question, not just when it *learns*, yields dramatic performance gains. This insight, operationalized in OpenAI's o1 model (September 2024) and its successors, restructured the entire industry's thinking about where to allocate resources.

Noam Brown, the OpenAI researcher behind these reasoning models, provided the clearest articulation. At NeurIPS 2024, he revealed that in his poker AI research, "by having the model think for 20 seconds in the middle of a hand, you get roughly the same improvement as scaling up the model size and training by **100,000x**." [[13]](#ref13) On the launch of o1 in September 2024, he wrote: "This opens up a new dimension for scaling. We're no longer bottlenecked by pretraining. We can now scale inference compute too." [[14]](#ref14) By April 2025, after releasing o3 and o4-mini, he stated: "There is still a lot of room to scale both of these further." [[15]](#ref15)

Jensen Huang seized on this shift as validation of exponentially growing compute demand. At GTC 2025, he declared: "The scaling law of AI is more resilient, and in fact, hyper-accelerated, and the amount of computation we need at this point, as a result of agentic AI and reasoning, is easily **100x more** than we thought we'd need at this time last year." By October 2025, Nvidia's stock rose after Huang stated AI computing demand was up "substantially." [[16]](#ref16) He predicted AI spending would increase **300%+ in three years** and described "two exponentials happening at the same time" — exponential demand and exponential compute needs. [[17]](#ref17)

The labs themselves diverge on how to frame this shift. Anthropic's Amodei pushed back on the idea that inference-time reasoning was revolutionary: "There's been this whole idea of reasoning models and test-time compute as if they're a totally different way of doing things. That's not our perspective. We see it more as a continuous spectrum." [[18]](#ref18) Meanwhile, he described the training-inference balance as an equilibrium problem: "Why doesn't everyone spend 100% of their compute on training? It's because if they didn't get any revenue, they couldn't raise money… As a stylized fact, it's 50%." [[19]](#ref19)

Altman acknowledged a more fundamental transition. At the Snowflake Summit in June 2025, he stated: "While we hit the training wall for AI in 2024, we continue to make progress on the inference side." He described the "platonic ideal" as "a very tiny model that has superhuman reasoning capabilities." [[20]](#ref20) Google's numbers illustrate the practical impact: Hassabis reported in July 2025 that Google processed "almost 1,000,000,000,000,000 tokens last month, more than double the amount from May." [[21]](#ref21)

The economic implications of reasoning models are revealing. The high-compute configuration of o3 consumed roughly **57 million tokens per question** (averaging 13.8 minutes of processing), versus 330,000 tokens in low-compute mode — a 172x compute difference. [[22]](#ref22) By late 2025, **inference surpassed training** in total data center revenue for the first time.

---

## When Executives Say AGI Is Coming, They Mean Different Things

The AGI timeline statements from major executives reveal as much about definitional strategy as about genuine prediction.

**Sam Altman (OpenAI):** His trajectory is the most striking. In September 2024, his essay "The Intelligence Age" predicted "superintelligence in a few thousand days." [[23]](#ref23) By January 2025, in his "Reflections" post, he escalated: "We are now confident we know how to build AGI as we have traditionally understood it." He told Bloomberg that AGI would "probably get developed during [Trump's] term" — by January 2029. Yet by August 2025, he was downplaying the concept entirely: "AGI has become a very sloppy term… I think it's not a super useful term." [[24]](#ref24)

**Dario Amodei (Anthropic):** The most consistent forecaster. His October 2024 essay "Machines of Loving Grace" predicted AI "smarter than a Nobel Prize winner across most relevant fields" could appear "as early as 2026." [[25]](#ref25) He described this as "a country of geniuses in a datacenter" — deliberately avoiding the AGI label, which he dismissed as "a marketing term." Through early 2026, his estimate remained stable at **2026–2027**. At Davos 2026, alongside Hassabis, he stated: "My guess is that we'll get that in 2026 or 2027."

**Demis Hassabis (Google DeepMind):** Consistently more cautious at **"five to ten years"** for a system exhibiting "all the cognitive capabilities humans can — and I mean all." At Davos 2026, he gave "roughly a 50% chance of achieving AGI by the end of the decade." [[26]](#ref26) He insists AGI will require "one or two more big breakthroughs" beyond current approaches — implicitly challenging the pure-scaling thesis. In an interview with Big Technology, he clarified what counts as AGI: it must exhibit creativity, long-horizon planning, and genuine scientific discovery. [[27]](#ref27)

**Satya Nadella (Microsoft):** The most intellectually honest framework. He rejected AGI benchmark claims as "nonsensical benchmark hacking" and proposed an **economic test**: "My formula for when can we say AGI has arrived? When, say, the developed world is growing at 10%." [[28]](#ref28) This implicitly pushes AGI far into the future while still justifying massive near-term investment.

**Yann LeCun (Meta):** The sharpest dissent. At CES in January 2025, he declared: "There's absolutely no way that autoregressive LLMs… will reach human intelligence. It's just not going to happen." He called LLMs fundamentally incapable of understanding causal relationships. [[29]](#ref29) At Davos 2026, he clashed publicly with Amodei and Hassabis over how close human-level AI really is. [[30]](#ref30)

**Elon Musk (xAI):** Predictions follow a pattern of serial optimism. In April 2024, claimed AGI would arrive "next year." When 2025 passed without that milestone, he pushed the timeline to **2026**, tied to Grok 5. [[31]](#ref31) His infrastructure commitments are real: xAI's **Colossus supercomputer**, built in 122 days with 200,000 Nvidia GPUs, with over $22 billion in primary funding. [[32]](#ref32)

**Ilya Sutskever (SSI):** Declared at NeurIPS 2024 that pre-training scaling has hit a wall ("the era of 'Just Add GPUs' is over") while predicting human-level AGI **within 5–20 years** via fundamentally new approaches. [[33]](#ref33) [[34]](#ref34)

**AGI Timeline Comparison:**

| Executive | Affiliation | Estimated Timeline | Key Qualifier |
|---|---|---|---|
| Sam Altman | OpenAI | ~2029 (or "already here") | Definitional retreat ongoing |
| Dario Amodei | Anthropic | 2026–2027 | "Nobel-level AI," not AGI |
| Demis Hassabis | Google DeepMind | 5–10 years; 50% by 2030 | Requires new breakthroughs |
| Satya Nadella | Microsoft | When GDP grows 10% | Economic, not technical, definition |
| Elon Musk | xAI | 2026 (currently) | Rolling 12-month prediction |
| Yann LeCun | Meta | Not with LLMs, ever | Architecturally skeptical |
| Ilya Sutskever | SSI | 5–20 years | New paradigm required |

---

## DeepSeek Cracked the Consensus — Then the Consensus Adapted

The release of **DeepSeek R1** on January 20, 2025 was the most disruptive single event in the AI industry's recent history. A Chinese lab achieved o1-level reasoning performance using cheaper H800 GPUs, a Mixture-of-Experts architecture (671 billion total parameters, 37 billion active per token), and claimed a final training cost of just **$5.6 million**. The model was released under an MIT open-source license. [[35]](#ref35)

The market reaction was visceral. On January 27, Nvidia lost approximately **$593 billion in market value** — the largest single-day corporate loss in U.S. history. The core fear: if frontier AI could be built for a fraction of assumed costs, the entire infrastructure buildout might be massively overscaled. [[36]](#ref36)

The industry's response revealed its adaptive capacity. Altman acknowledged DeepSeek R1 as "impressive" but doubled down: "We believe more compute is more important now than ever before." [[37]](#ref37) Huang called the market's interpretation "exactly the opposite" of correct, arguing that efficiency gains would increase total demand via **Jevons Paradox**. [[38]](#ref38) Nvidia officially framed DeepSeek as "an excellent AI advancement and a perfect example of Test Time Scaling." [[39]](#ref39)

The full-cost debate matters. While DeepSeek's $5.6 million figure covers only the final successful training run, industry analysts estimated total development costs including R&D and failed experiments at approximately **$100 million** — still roughly one-tenth of what Western labs spent on comparable models. [[40]](#ref40)

Crucially, **no major hyperscaler cut capex plans** in response. What shifted was the *composition* of investment — toward inference-optimized infrastructure — and the rhetorical emphasis on algorithmic efficiency alongside raw scale.

---

## The $600 Billion Question Remains Unanswered

The skeptical case against the AI infrastructure buildout has not been refuted — it has simply been outspent. Sequoia partner David Cahn identified a **$600 billion annual gap** between AI infrastructure spending and AI revenue in June 2024, a figure that widened rather than narrowed through 2025. [[41]](#ref41) Goldman Sachs published a June 2024 report titled "Gen AI: Too Much Spend, Too Little Benefit?" in which head of equity research Jim Covello argued the technology was "exceptionally expensive" and questions remained about whether it could "solve complex problems."

The enterprise adoption data lends ammunition to skeptics. U.S. Census Bureau data from March 2024 showed AI adoption at just **5.4% of businesses**. Only roughly 3% of consumers pay for AI services. Even believers acknowledge the risks: Altman admitted some AI startup valuations are "insane" and that "irrational behavior" characterizes parts of the market. Pichai acknowledged "elements of irrationality" in a November 2025 BBC interview.

The counterargument rests on two pillars. First, **demand signals are genuinely strong**: every hyperscaler reports being capacity-constrained, with Google's cloud backlog growing 55% quarter-over-quarter to **$240 billion** and AWS backlog reaching $244 billion. Second, infrastructure retains value even if AI progress slows. Andy Jassy framed Amazon's record spending explicitly: "This isn't some sort of quixotic, top-line grab. We have confidence that these investments will yield strong returns." [[2]](#ref2)

---

## Conclusion: Conviction, Compulsion, and the Fog of an Arms Race

Three dynamics define this moment. First, the **intellectual framework has fractured**: the clean narrative of "scale pre-training and AGI follows" has given way to a multi-dimensional optimization across pre-training, post-training reinforcement learning, and inference-time compute, with genuine disagreement about whether current architectures can reach human-level intelligence at all.

Second, **competitive game theory now dominates capital allocation** more than any bottom-up ROI calculation. Pichai's "risk of underinvesting" formulation became the industry's defining rationale not because it resolves the economic uncertainty but because it reframes the question: from "will this investment generate adequate returns?" to "can we afford to let competitors build this first?"

Third, the **AGI timeline discourse serves a dual function** as both genuine forecast and capital-formation narrative. Nadella's economic definition of AGI is perhaps the most revealing: it acknowledges that the technical milestone matters less than the economic transformation it produces, and implicitly concedes that transformation may take far longer than the current investment pace assumes.

What remains genuinely uncertain is not whether AI will be transformative — the capabilities demonstrated from 2024 through early 2026 leave little doubt — but whether the **timing and magnitude of economic returns** will match the timing and magnitude of infrastructure commitments now exceeding half a trillion dollars annually.

---

## References

1. <a name="ref1"></a>CNBC — [Why Amazon's CEO is 'confident' with $200 billion spending plan](https://www.cnbc.com/2026/02/05/why-amazons-ceo-is-confident-with-200-billion-spending-plan.html) (Feb 2026)
2. <a name="ref2"></a>AI Magazine — [Why Amazon is the Latest Tech Giant to Bet Big on AI](https://aimagazine.com/news/amazon-ceo-andy-jassy-on-ai-investment-2026) (2026)
3. <a name="ref3"></a>The Motley Fool — [Alphabet Q4 2024 Earnings Call Transcript](https://www.fool.com/earnings/call-transcripts/2025/02/05/alphabet-goog-q4-2024-earnings-call-transcript/) (Feb 2025)
4. <a name="ref4"></a>CNBC — [Meta's Zuckerberg gets green light from Wall Street to keep pouring money into AI](https://www.cnbc.com/2026/01/28/metas-zuckerberg-gets-green-light-from-wall-street-to-invest-in-ai.html) (Jan 2026)
5. <a name="ref5"></a>Data Center Dynamics — [Meta plans "notably larger" capex spend on AI data centers in 2026](https://www.datacenterdynamics.com/en/news/meta-plans-notably-larger-capex-spend-on-ai-data-centers-in-2026-compute-expectations-already-higher-than-last-quarter-prediction/) (2026)
6. <a name="ref6"></a>Sam Altman — [Three Observations](https://blog.samaltman.com/three-observations) (Feb 2025)
7. <a name="ref7"></a>Bloomberg — [OpenAI's Sam Altman Expects to Spend 'Trillions' on Infrastructure](https://www.bloomberg.com/news/articles/2025-08-15/openai-s-altman-expects-to-spend-trillions-on-infrastructure) (Aug 2025)
8. <a name="ref8"></a>OpenAI — [Announcing The Stargate Project](https://openai.com/index/announcing-the-stargate-project/) (Jan 2025)
9. <a name="ref9"></a>OpenAI — [OpenAI, Oracle, and SoftBank expand Stargate with five new AI data center sites](https://openai.com/index/five-new-stargate-sites/) (2025)
10. <a name="ref10"></a>Axios — [OpenAI wants to get to $1 trillion a year in infrastructure spend, Altman says](https://www.axios.com/2025/10/28/openai-1-trillion-altman) (Oct 2025)
11. <a name="ref11"></a>Fortune — [Anthropic CEO Dario Amodei explains his spending caution](https://fortune.com/2026/02/14/anthropic-ceo-dario-amodei-spending-capex-risk-ai-revenue-forecasts-bankruptcy/) (Feb 2026)
12. <a name="ref12"></a>BeBeez International — [Anthropic closes a $30bn Series G round](https://bebeez.eu/2026/02/16/ai-giant-anthropic-closes-a-30bn-series-g-round-and-is-now-valued-at-380bn/) (Feb 2026)
13. <a name="ref13"></a>JolTML — [NeurIPS 2024: Math-AI, Noam Brown & Panel](https://joltml.com/neurips-2024/math-ai-noam-brown-panel/) (Dec 2024)
14. <a name="ref14"></a>X (Twitter) — [Noam Brown on o1 inference scaling](https://x.com/polynoamial/status/1834280425457426689) (Sep 2024)
15. <a name="ref15"></a>X (Twitter) — [Noam Brown on o3 and o4-mini](https://x.com/polynoamial/status/1912564068168450396) (Apr 2025)
16. <a name="ref16"></a>CNBC — [Nvidia shares rise after CEO Huang says AI computing demand is up 'substantially'](https://www.cnbc.com/2025/10/08/jensen-huang-nvidia-computing-demand.html) (Oct 2025)
17. <a name="ref17"></a>IO Fund — [Nvidia CEO Predicts AI Spending Will Increase 300%+ in 3 Years](https://io-fund.com/semiconductors/data-center/nvidia-ceo-predicts-ai-spending-will-increase-300-percent-in-3-years) (2025)
18. <a name="ref18"></a>X (Twitter) — [Nathan Lambert quoting Dario Amodei on reasoning models](https://x.com/natolambert/status/1882286138532270151) (Jan 2025)
19. <a name="ref19"></a>Singju Post — [Anthropic CEO Dario Amodei's Interview on Dwarkesh Podcast (Transcript)](https://singjupost.com/anthropic-ceo-dario-amodeis-interview-on-dwarkesh-podcast-transcript/) (2025)
20. <a name="ref20"></a>HPCwire — [AI Agents to Drive Scientific Discovery Within a Year, Altman Predicts](https://www.hpcwire.com/2025/06/04/ai-agents-to-drive-scientific-discovery-within-a-year-altman-predicts/) (Jun 2025)
21. <a name="ref21"></a>Data Center Dynamics — [Google processed nearly one quadrillion tokens in June, DeepMind's Demis Hassabis says](https://www.datacenterdynamics.com/en/news/google-processed-nearly-one-quadrillion-tokens-in-june-deepminds-demis-hassabis-says/) (Jul 2025)
22. <a name="ref22"></a>TechCrunch — [OpenAI's o3 suggests AI models are scaling in new ways — but so are the costs](https://techcrunch.com/2024/12/23/openais-o3-suggests-ai-models-are-scaling-in-new-ways-but-so-are-the-costs/) (Dec 2024)
23. <a name="ref23"></a>Sam Altman — [The Intelligence Age](https://ia.samaltman.com/) (Sep 2024)
24. <a name="ref24"></a>CNBC — [Sam Altman says AGI has become a pointless term — experts agree](https://www.cnbc.com/2025/08/11/sam-altman-says-agi-is-a-pointless-term-experts-agree.html) (Aug 2025)
25. <a name="ref25"></a>Dario Amodei — [Machines of Loving Grace](https://www.darioamodei.com/essay/machines-of-loving-grace) (Oct 2024)
26. <a name="ref26"></a>CNBC — [AI that can match humans at any task will be here in five to 10 years, Google DeepMind CEO says](https://www.cnbc.com/2025/03/17/human-level-ai-will-be-here-in-5-to-10-years-deepmind-ceo-says.html) (Mar 2025)
27. <a name="ref27"></a>Big Technology — [Google DeepMind CEO Demis Hassabis on AI's Next Breakthroughs](https://www.bigtechnology.com/p/google-deepmind-ceo-demis-hassabis-946) (2025)
28. <a name="ref28"></a>GeekWire — [Microsoft CEO Satya Nadella has a formula to gauge the long-term success of AI investments](https://www.geekwire.com/2025/microsoft-ceo-satya-nadella-has-a-formula-to-gauge-the-long-term-success-of-ai-investments/) (2025)
29. <a name="ref29"></a>PYMNTS — [Meta Chief AI Scientist Slams Quest for Human-Level Intelligence](https://www.pymnts.com/artificial-intelligence-2/2025/meta-large-language-models-will-not-get-to-human-level-intelligence/) (2025)
30. <a name="ref30"></a>Fortune — [AI luminaries at Davos clash over how close human-level intelligence really is](https://fortune.com/2026/01/23/deepmind-demis-hassabis-anthropic-dario-amodei-yann-lecun-ai-davos/) (Jan 2026)
31. <a name="ref31"></a>Gizmodo — [Elon Musk Predicts AGI by 2026 (He Predicted AGI by 2025 Last Year)](https://gizmodo.com/elon-musk-predicts-agi-by-2026-he-predicted-agi-by-2025-last-year-2000701007) (Dec 2025)
32. <a name="ref32"></a>xAI — [Colossus Supercomputer](https://x.ai/colossus) (2024)
33. <a name="ref33"></a>The Decoder — [OpenAI co-founder Sutskever predicts a new AI "age of discovery" as LLM scaling hits a wall](https://the-decoder.com/openai-co-founder-predicts-a-new-ai-age-of-discovery-as-llm-scaling-hits-a-wall/) (Nov 2024)
34. <a name="ref34"></a>36Kr — [Ilya Sutskever's 1.5-Hour Conversation After Leaving OpenAI: AGI Achievable in Just 5 Years](https://eu.36kr.com/en/p/3570122305223553) (2025)
35. <a name="ref35"></a>NPR — [DeepSeek: Did a little-known Chinese startup cause a 'Sputnik moment' for AI?](https://www.npr.org/2025/01/28/g-s1-45061/deepseek-did-a-little-known-chinese-startup-cause-a-sputnik-moment-for-ai) (Jan 2025)
36. <a name="ref36"></a>FinancialContent — [The DeepSeek-R1 Effect: How a $6 Million Model Shattered the AI Scaling Myth](https://markets.financialcontent.com/stocks/article/tokenring-2026-2-6-the-deepseek-r1-effect-how-a-6-million-model-shattered-the-ai-scaling-myth) (Feb 2026)
37. <a name="ref37"></a>TechRadar — [OpenAI's Sam Altman calls DeepSeek 'impressive' but promises to launch 'much better models' soon](https://www.techradar.com/computing/artificial-intelligence/openais-sam-altman-calls-deepseek-impressive-but-promises-to-launch-much-better-models-soon) (Jan 2025)
38. <a name="ref38"></a>Yahoo Finance — [Nvidia CEO Jensen Huang says market got it wrong about DeepSeek's impact](https://finance.yahoo.com/news/nvidia-ceo-jensen-huang-says-203600486.html) (Jan 2025)
39. <a name="ref39"></a>CNBC — [Nvidia calls China's DeepSeek R1 model 'an excellent AI advancement'](https://www.cnbc.com/2025/01/27/nvidia-calls-chinas-deepseek-r1-model-an-excellent-ai-advancement.html) (Jan 2025)
40. <a name="ref40"></a>CSIS — [DeepSeek's Latest Breakthrough Is Redefining the AI Race](https://www.csis.org/analysis/deepseeks-latest-breakthrough-redefining-ai-race) (2025)
41. <a name="ref41"></a>AI Insider — [Updated Analysis Shows AI Revenue Gap Has Soared to $600 Billion](https://theaiinsider.tech/2024/07/07/updated-analysis-shows-ai-revenue-gap-has-soared-to-600-billion/) (Jul 2024)
42. <a name="ref42"></a>NPR — [Here's why concerns about an AI bubble are bigger than ever](https://www.npr.org/2025/11/23/nx-s1-5615410/ai-bubble-nvidia-openai-revenue-bust-data-centers) (Nov 2025)
43. <a name="ref43"></a>Fortune — [Alphabet is confident about plans to double capex spending](https://fortune.com/2026/02/04/alphabet-google-ai-spending-supply-constraints/) (Feb 2026)
44. <a name="ref44"></a>Dario Amodei — [The Adolescence of Technology](https://www.darioamodei.com/essay/the-adolescence-of-technology) (2026)
45. <a name="ref45"></a>Sam Altman — [Reflections](https://blog.samaltman.com/reflections) (Jan 2025)
