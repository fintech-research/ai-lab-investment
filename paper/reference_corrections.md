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

---
---

# Second Audit — Pre-Submission (issue #127 / M16)

**Date:** 2026-07-25
**Scope:** every entry in `references.bib` (65 entries after the #104 trim and the
#122 additions), with full manual verification of all working-paper, preprint,
industry, blog, and interview entries, plus a Crossref/RePEc spot-check of every
journal entry not already verified in the 2026-02-24 audit or in #122.
**Sources of record:** NBER paper pages, arXiv abstract pages + API,
`api.crossref.org`, IDEAS/RePEc (EconPapers), and the publishers' own pages for
the blog/industry items.

Note: several entries discussed in the first audit (`sevilla2022compute`,
`epoch2024trends`, `nishihara2021optimal`, `jones2023agi`, `musk2026*`,
`goldstein2001ebit`, `aghion1992model`, `hayashi1982tobin`) no longer exist —
they were removed when the bibliography was trimmed from 76 to 57 entries
(commit `4f2e938`, #104). The flagged/likely-hallucinated `nishihara2021optimal`
is therefore resolved by deletion.

## Corrections Made

### 1. `eisfeldt2024generative` → `eisfeldt2023generative` — author list, entry type, key/year

**Before:** `@article`, `author={Eisfeldt, Andrea L. and Schubert, Gregor and Taska, Bledi and Zhang, Miao Ben}`, `journal={NBER Working Paper No. 31222}`, `year={2023}`, key says 2024.
**After:** `@techreport`, `author={Eisfeldt, Andrea L. and Schubert, Gregor and Zhang, Miao Ben}`, `institution={National Bureau of Economic Research}`, `type={NBER Working Paper}`, `number={31222}`, `address={Cambridge, MA}`, `year={2023}`, `month={May}`, `note={Revised January 2026}`; key renamed to `eisfeldt2023generative`.

The current NBER record for WP 31222 (fetched 2026-07-25) lists **three** authors —
Andrea L. Eisfeldt, Gregor Schubert, Miao Ben Zhang — issue date May 2023,
revision date January 2026. Bledi Taska was an author of the original May 2023
version but is not on the current record. The `journal` field was being abused
for the working-paper number; a `@techreport` renders correctly under
`econometrica.bst`. The key/year mismatch is resolved by renaming the key to
match the issue year. Only in-text use is `_literature.qmd:26`, updated. Still no
published journal version as of the check date.

### 2. `korinek2024scenarios` — entry type (same `journal`-field abuse)

**Before:** `@article` with `journal={NBER Working Paper No. 32255}`.
**After:** `@techreport` with `institution`, `type={NBER Working Paper}`, `number={32255}`, `address={Cambridge, MA}`, `month={March}`.

Content verified against the NBER page: title, both authors (Korinek and Suh),
WP 32255, issued March 2024, no revision, no published version noted. Only the
entry type changed.

### 3. `deepseek2025r1` — spurious colon in title

**Before:** `title={{DeepSeek-R1}: Incentivizes Reasoning in {LLMs} Through Reinforcement Learning}`
**After:** `title={{DeepSeek-R1} Incentivizes Reasoning in {LLMs} Through Reinforcement Learning}`

The published Nature title is a sentence, not a title–subtitle pair: "DeepSeek-R1
incentivizes reasoning in LLMs through reinforcement learning." The colon made
the verb read as the start of a subtitle. Everything else verified against
Crossref for DOI 10.1038/s41586-025-09422-z: *Nature* **645**(8081):633–638,
17 September 2025, first authors Guo, Yang, Zhang, Song, Wang (190 authors
total, so `and others` is correct). The published-version check requested in the
review is therefore satisfied: the entry already pointed at the Nature version.

### 4. `cahn2024gap` — wrong month

**Before:** `month={July}` — **After:** `month={June}`

Sequoia Capital's page dates "AI's $600B Question" to **20 June 2024**. Title,
author (David Cahn), publisher, and URL verified and unchanged.

### 5. `tullock1980efficient` — wrong entry type (book chapter cited as journal article)

**Before:** `@article` with `journal={Toward a Theory of the Rent-Seeking Society}`.
**After:** `@incollection` with `booktitle={Toward a Theory of the Rent-Seeking Society}`, `editor={Buchanan, James M. and Tollison, Robert D. and Tullock, Gordon}`, `publisher={Texas A\&M University Press}`, `address={College Station, TX}`.

"Efficient Rent Seeking" is a chapter in the Buchanan–Tollison–Tullock edited
volume (Texas A&M University Press, 1980), pp. 97–112 — not a journal article.
Pages and year were correct.

## Working Papers, Preprints, Industry and Blog Entries — Full Audit

| Key | Type | Verdict | Record consulted |
|-----|------|---------|------------------|
| `eisfeldt2023generative` | NBER WP | **Corrected** (see 1) | nber.org/papers/w31222 |
| `korinek2024scenarios` | NBER WP | **Corrected** (type only; content verified) | nber.org/papers/w32255 |
| `deepseek2025r1` | Journal (was preprint) | **Corrected** (title punctuation); Nature version confirmed | Crossref 10.1038/s41586-025-09422-z |
| `cahn2024gap` | Industry (Sequoia) | **Corrected** (month) | sequoiacap.com, URL 200 OK |
| `kaplan2020scaling` | arXiv preprint | Verified unchanged — arXiv 2001.08361, submitted 23 Jan 2020, 10 authors (Kaplan, McCandlish, Henighan, Brown, Chess first five), **no journal reference** | arXiv API |
| `sastry2024computing` | arXiv preprint | Verified unchanged — arXiv 2402.08797, submitted 13 Feb 2024, 19 authors (Sastry, Heim, Belfield, Anderljung, Brundage first five), v1 only, no published version | arxiv.org/abs/2402.08797 |
| `hoffmann2022training` | Conference proceedings | Verified unchanged — NeurIPS 35:30016–30030 (2022); 22 authors, first five match | Crossref 10.52202/068431-2176 |
| `amodei2026dwarkesh` | Interview | Verified unchanged — Dwarkesh Podcast, "Dario Amodei — 'We are near the end of the exponential'", 13 February 2026; URL 200 OK | dwarkesh.com |
| `amodei2024machines` | Online essay | Verified unchanged — URL 200 OK, October 2024 | darioamodei.com |
| `altman2025observations` | Blog post | Verified unchanged — URL 200 OK; page carries no visible date, February 2025 attribution retained (widely reported date, 9 Feb 2025) | blog.samaltman.com |
| `altman2024intelligence` | Online essay | Verified unchanged — URL 200 OK, September 2024 | ia.samaltman.com |

All five external URLs return HTTP 200 (checked 2026-07-25). No dataset entries
exist in the bibliography.

## Journal / Book Entries — Spot-Check of Everything Not Previously Verified

Verified against Crossref and/or IDEAS/RePEc; all fields (authors, title,
journal, volume, issue, pages, year) match the entry unless noted.

| Key | Record | Verdict |
|-----|--------|---------|
| `blackcox1976valuing` | JF 31(2):351–367, 1976 | Verified unchanged |
| `berk1999optimal` | JF 54(5):1553–1607, 1999 | Verified unchanged |
| `skaperdas1996contest` | Economic Theory 7(2):283–290, 1996 | Verified unchanged |
| `pindyck1988irreversible` | AER 78(5):969–985, 1988 | Verified unchanged |
| `bernanke1983irreversibility` | QJE 98(1):85–106, 1983 | Verified unchanged |
| `grenadier2011real` | RFS 24(12):3993–4036, 2011 | Verified unchanged |
| `kumar2018optimal` | RFS 31(9):3452–3490, 2018 | Verified unchanged |
| `bolton2019investment` | JET 184:104912, 2019 | Verified unchanged |
| `jovanovic2005general` | Handbook of Economic Growth, 1181–1224, 2005 | Verified unchanged |
| `bloom2020ideas` | AER 110(4):1104–1144, 2020 | Verified unchanged |
| `akcigit2018growth` | JPE 126(4):1374–1443, 2018 | Verified unchanged |
| `weeds2002strategic` | RES 69(3):729–747, 2002 | Verified unchanged |
| `lambrecht2003real` | JEDC 27(4):619–643, 2003 | Verified unchanged |
| `katz1986technology` | JPE 94(4):822–841, 1986 | Verified unchanged |
| `farrell1986installed` | AER 76(5):940–955, 1986 | Verified unchanged (RePEc `aea:aecrev:v:76:y:1986:i:5:p:940-55`) |
| `decamps2006irreversible` | Economic Theory 28(2):425–448, 2006 | Verified unchanged |
| `loury1979market` | QJE 93(3):395–410, 1979 | Verified unchanged |
| `reinganum1982strategic` | Econometrica 50(3):671–688, 1982 | Verified unchanged |
| `harris1987racing` | RES 54(1):1–21, 1987 | Verified unchanged |
| `grossman1986optimal` | RAND JE 17(4):581–593, 1986 | Verified unchanged |
| `scheinkman2003overconfidence` | JPE 111(6):1183–1219, 2003 | Verified unchanged — see note below |
| `harrison1978speculative` | QJE 92(2):323–336, 1978 | Verified unchanged |
| `gornall2020squaring` | JFE 135(1):120–143, 2020 | Verified unchanged |
| `tullock1980efficient` | Buchanan–Tollison–Tullock volume, 97–112, 1980 | **Corrected** (entry type; see 5) |
| `guo2005investment` | JET 122(1):37–59, 2005 | Verified unchanged (re-confirms first audit) |
| `bouis2009multistage` | IJIO 27:320–331, 2009 | Verified unchanged (re-confirms first audit) |
| `hackbarth2012corporate` | RFS 25(3):747–796, 2012 | Verified unchanged (re-confirms first audit) |
| `jones2024agi` | AER:Insights 6(4):575–590, 2024 | Verified unchanged (re-confirms first audit) |
| `acemoglu2024simple` | Economic Policy 40(121):13–58, 2025 | Verified unchanged (re-confirms first audit) |
| `babina2024artificial` | JFE 151:103745, 2024 | Verified unchanged |
| `jones1995rdbased` | JPE 103(4):759–784, 1995 | Verified unchanged |
| `agrawal2019economics` | Univ. of Chicago Press, 2019 | Verified unchanged |
| `dixit1994investment` | Princeton University Press, 1994 | Verified unchanged |

`scheinkman2003overconfidence` note: RePEc records the page range as 1183–1219
(matching the entry and the deliberate fix in commit `f15bfe5`), while Crossref's
University of Chicago Press deposit says 1183–1220. The RePEc/entry value is
retained.

The eight entries added in #122 — `hackbarth2006capital`, `chen2010macroeconomic`,
`bhamra2010levered`, `aguerrevere2003equilibrium`, `aguerrevere2009real`,
`vanmieghem2003capacity`, `chod2005resource`, `aghion2019artificial` — were
verified against Crossref at the time they were added and are logged here as
verified; they were not re-checked.

The entries in the first audit's "Entries Confirmed Correct" table that survive
the #104 trim (`mcdonald1986value`, `brennan1985evaluating`, `huisman2015strategic`,
`grenadier2002option`, `fudenberg1985preemption`, `novymarx2007operating`,
`pawlina2006real`, `leland1994corporate`, `leland1996optimal`, `merton1974pricing`,
`hackbarth2014capital`, `sundaresan2015dynamic`, `bloom2009impact`) carry forward
their earlier verification.

## Flagged / Residual Items

- `acemoglu2024simple` — the citation key says 2024 but the entry (correctly)
  carries `year={2025}`, the *Economic Policy* print year. The key was left alone
  to avoid churning cross-references for a purely cosmetic label; the rendered
  citation reads "Acemoglu (2025)", which is what matters.
- `kaplan2020scaling` uses `@article` with `journal={arXiv preprint arXiv:2001.08361}`
  while `sastry2024computing` uses `@misc` with `eprint`/`archivePrefix`. Both
  render acceptably under `econometrica.bst`; the inconsistency is cosmetic and
  was left in place.
- `altman2025observations` carries no visible date on the page itself; the
  February 2025 attribution rests on secondary reporting rather than the source.

## Build Fix

`reference_corrections.md` (this file), `AGENTS.md`, and `CLAUDE.md` were being
rendered as extra HTML/PDF outputs by the identified profile, whose render list
included `"*.md"`. The list in `_quarto-identified.yml` is now `"*.qmd"` minus
`index-blind.qmd`, and the stale outputs were deleted from `paper/_output/`. The
blind profile (`_quarto-blind.yml`) renders only `index-blind.qmd` and was never
affected.
