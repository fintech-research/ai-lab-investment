# Bibliography Validation Report

**Date:** 2026-02-24
**Method:** Systematic verification of all entries in `references.bib` against Google Scholar, IDEAS/RePEC, and publisher databases (ScienceDirect, Oxford Academic, AEA, NBER).

---

## Summary

Of the ~78 entries in `references.bib`, 10 had errors ranging from wrong titles and page numbers to unconfirmed publications and missing co-authors. All confirmed errors have been corrected in the file. One entry could not be verified at all and is flagged with a warning comment.

---

## Corrections Made

### 1. `guo2005investment` — Wrong title

**Before:** `title={Investment under Regime Switching}`
**After:** `title={Irreversible Investment with Regime Shifts}`

The actual paper is Guo, Miao & Morellec (2005), "Irreversible Investment with Regime Shifts," *Journal of Economic Theory* 122(1):37–59. Journal, volume, and pages were correct.

---

### 2. `bouis2009multistage` — Wrong title and wrong pages

**Before:** `title={A Multiperiod Entry Game with Learning and Preemption}`, `pages={615--625}`
**After:** `title={Investment in Oligopoly under Uncertainty: The Accordion Effect}`, `pages={320--331}`

The actual paper by Bouis, Huisman & Kort (2009) is titled "Investment in oligopoly under uncertainty: The accordion effect," *International Journal of Industrial Organization* 27:320–331. The original title and page range are entirely fabricated.

---

### 3. `sevilla2022compute` — Wrong venue; also changed entry type to `@inproceedings`

**Before:** `journal={2022 IEEE/ACM International Conference on Big Data Computing}` (type `@article`)
**After:** `booktitle={2022 International Joint Conference on Neural Networks ({IJCNN})}` (type `@inproceedings`)

The paper by Sevilla et al. was presented at **IJCNN 2022** (IEEE), not at an "IEEE/ACM International Conference on Big Data Computing" (which is a different, unrelated conference series). The title and author list were correct.

---

### 4. `jones2024agi` — Fabricated NBER number; paper is actually published

**Before:** `journal={NBER Working Paper No. 32797}`, `year={2024}`
**After:** Published journal citation — `journal={American Economic Review: Insights}`, `volume={6}`, `number={4}`, `pages={575--590}`, `year={2024}`

NBER Working Paper 32797 does not correspond to this paper (the original WP is No. 31837, captured in the separate entry `jones2023agi`). The paper was published as Jones, C.I. (2024), "The A.I. Dilemma: Growth versus Existential Risk," *AER: Insights* 6(4):575–590. DOI: 10.1257/aeri.20230570.

Note: `jones2023agi` (NBER WP 31837, 2023) is the correct working paper citation and was left unchanged.

---

### 5. `acemoglu2024simple` — Working paper now published

**Before:** `journal={NBER Working Paper No. 32487}`, `year={2024}`
**After:** `journal={Economic Policy}`, `volume={40}`, `number={121}`, `pages={13--58}`, `year={2025}`

Published as Acemoglu, D. (2025), "The Simple Macroeconomics of AI," *Economic Policy* 40(121):13–58 (first published online August 2024; print issue January 2025). DOI: 10.1093/epolic/eiae042.

---

### 6. `korinek2024scenarios` — Missing co-author

**Before:** `author={Korinek, Anton}`
**After:** `author={Korinek, Anton and Suh, Donghyun}`

The paper is co-authored with Donghyun Suh. Still a working paper (NBER WP 32255); no journal publication found as of the check date.

---

### 7. `eisfeldt2024generative` — JFE publication unconfirmed; missing co-author; wrong year

**Before:** `journal={Journal of Financial Economics}`, `volume={162}`, `pages={103898}`, `year={2024}`, authors: Eisfeldt, Schubert, Zhang
**After:** `journal={NBER Working Paper No. 31222}`, `year={2023}`, authors: Eisfeldt, Schubert, Taska, Zhang

No published JFE version (vol. 162, article 103898) could be confirmed across Google Scholar, ScienceDirect, or NBER. All academic citations found across the literature reference this as NBER WP 31222 (May 2023). The fourth co-author, **Bledi Taska**, was missing from the original entry. Changed to working paper citation. **Action required:** verify publication status before final submission — if it has appeared in JFE, update accordingly.

---

### 8. `epoch2024trends` — Not a formal paper; changed to `@misc`

**Before:** `@article` with `journal={Epoch AI Research Report}`
**After:** `@misc` pointing to `https://epoch.ai/blog/trends-in-machine-learning-hardware`

"Epoch AI Research Report" is not a journal; the content corresponds to a blog post/online data report by Epoch AI. Changed to a `@misc` entry. The title was also slightly adjusted to match the actual blog post title ("Trends in Machine Learning Hardware"). **Action required:** confirm which specific Epoch AI resource is intended and update the URL accordingly.

---

### 9. `hackbarth2012corporate` — Completely wrong entry (title, issue, pages all wrong)

**Before:** `title={Corporate Investment and Financing Dynamics}`, `number={5}`, `pages={1501--1543}`
**After:** `title={Optimal Priority Structure, Capital Structure, and Investment}`, `number={3}`, `pages={747--796}`

The only Hackbarth & Mauer paper in the *Review of Financial Studies* (2012) is "Optimal Priority Structure, Capital Structure, and Investment," RFS 25(3):747–796. The title "Corporate Investment and Financing Dynamics" belongs to a 2024 paper by Hackbarth & **Sun** in *Review of Corporate Finance Studies* 13(3):625–667 — a completely different paper. The original entry appears to conflate two unrelated papers.

---

## Flagged Entry — Requires Manual Review

### 10. `nishihara2021optimal` — Cannot be verified; likely hallucinated

Entry: Nishihara, Michi and Ohyama, Atsuyuki. "Optimal Investment Timing with Regime Switching." *Journal of Economic Dynamics and Control* 125:104096, 2021.

**No paper matching this description was found** on Google Scholar, IDEAS/RePEC, ScienceDirect (JEDC vol. 125), or Nishihara's faculty page at Osaka University. Nishihara's only 2021 JEDC paper found is "Optimal capital structure and simultaneous bankruptcy of firms in corporate networks" (co-authored with Shibata, JEDC 133:104264, 2021). Nishihara and Ohyama have collaborated, but their joint work dates to 2007–2008 and concerns R&D competition, not investment timing with regime switching.

**A warning comment has been added to the bib entry.** This reference should either be removed or replaced with a verified substitute before submission.

---

## Entries Confirmed Correct (Representative Sample)

The following were spot-checked and confirmed accurate:

| Key | Authors | Journal | Vol/Pages | Year |
|-----|---------|---------|-----------|------|
| `mcdonald1986value` | McDonald & Siegel | QJE | 101(4):707–727 | 1986 |
| `brennan1985evaluating` | Brennan & Schwartz | JB | 58(2):135–157 | 1985 |
| `huisman2015strategic` | Huisman & Kort | RAND JE | 46(2):376–408 | 2015 |
| `grenadier2002option` | Grenadier | RFS | 15(3):691–721 | 2002 |
| `fudenberg1985preemption` | Fudenberg & Tirole | RES | 52(3):383–401 | 1985 |
| `novymarx2007operating` | Novy-Marx | RFS | 20(5):1461–1502 | 2007 |
| `pawlina2006real` | Pawlina & Kort | JEMS | 15(1):1–35 | 2006 |
| `leland1994corporate` | Leland | JF | 49(4):1213–1252 | 1994 |
| `leland1996optimal` | Leland & Toft | JF | 51(3):987–1019 | 1996 |
| `merton1974pricing` | Merton | JF | 29(2):449–470 | 1974 |
| `goldstein2001ebit` | Goldstein, Ju & Leland | JB | 74(4):483–512 | 2001 |
| `hoffmann2022training` | Hoffmann et al. | NeurIPS | 35:30016–30030 | 2022 |
| `babina2024artificial` | Babina et al. | JFE | 151:103745 | 2024 |
| `hackbarth2014capital` | Hackbarth, Mathews & Robinson | MS | 60(12):2971–2993 | 2014 |
| `sundaresan2015dynamic` | Sundaresan, Wang & Yang | RCFS | 4(1):1–42 | 2015 |
| `bloom2009impact` | Bloom | Econometrica | 77(3):623–685 | 2009 |
| `aghion1992model` | Aghion & Howitt | Econometrica | 60(2):323–351 | 1992 |
| `jones1995rdbased` | Jones | JPE | 103(4):759–784 | 1995 |
| `hayashi1982tobin` | Hayashi | Econometrica | 50(1):213–224 | 1982 |

---

## Notes on Working Papers

The following NBER working papers were checked and remain unpublished as of 2026-02-24:

- `jones2023agi` — NBER WP 31837 (Jones, 2023). The published version is captured in `jones2024agi` (now corrected to AER:Insights).
- `korinek2024scenarios` — NBER WP 32255 (Korinek & Suh, 2024). Still a working paper.

---

## Misc/Industry References

The misc entries (executive quotes, blog posts, earnings calls) were not subject to the same verification standard. One observation:

- `musk2026agi` and `musk2026colossus` are cited with `year={2026}`. Based on the embedded timestamps in the X/Twitter post IDs (1875339801617764644 and 1947701807389515912), these posts may date to January 2025 and July 2025 respectively, not January 2026. **Recommend verifying the dates of these tweets directly.**
