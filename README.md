# A Drosophila connectome substrate inside an LLM agent

**Evidence package** for the preprint. Every figure and every table in `paper/` is
re-derivable from `data/` by `code/paper_draft_v7.py` (English) and
`code/paper_draft_v7_zh.py` (Chinese). The ledgers are shipped byte-identical to the ones
the paper read.

Preprint: **DOI [10.5281/zenodo.23402098](https://doi.org/10.5281/zenodo.23402098)**
(v7, published 2026-10-16, resource type Preprint, CC BY 4.0; the English and Chinese
editions are the two files of that record, and both are also in `paper/`). All versions:
**DOI [10.5281/zenodo.23396755](https://doi.org/10.5281/zenodo.23396755)**.

> Luan, B. (2026). *A Drosophila connectome substrate inside an LLM agent: what it gates,
> what it does not, and what it costs* (Version v7). Zenodo.
> https://doi.org/10.5281/zenodo.23402098 — author ORCID 0009-0001-5836-2923

## What v7 added

Every control arm and the real-brain lineage now run on a **third seed**, which moves two
sentences and leaves the rest of the ordering intact:

- `data/mac/ctrl/s13/` — seed 13: the three lesion arms and the unmodified brain, selection
  lineage and random control, eight ledgers. Seed 11 ran on this machine's CPU, seeds 12 and
  13 on a rented cloud GPU under the same CUDA numerical path as the GPU host, so agreement
  across the three seeds is agreement across devices as well.
- `code/ctrl_run.py` — the runner that produced the control arms, with one defect fixed. It
  hardcoded the output directory and ignored the environment, so a run pointed at a new seed
  wrote over the previous seed's ledgers in the default directory (the seed-13 arms landed in
  the seed-11 directory on the run host; the shipped seed-11 ledgers were written on a
  different machine and are untouched). `OUTD` is honoured now, the way `real_run.py` honours
  it, and a short run with `POP=6 GENS=1 ROUNDS=10` into a scratch directory confirms the
  ledgers land where `OUTD` says.
- **A bound we published in v5 is falsified by our own new data.** v5 wrote that inside an
  arm the two lineages diverge more than the seeds do. On three seeds the coin arm's
  across-seed spread (**465**) exceeds its largest within-arm divergence (**243**); the
  lesioned arm reads 159 against 152 and the rewired arm 58 against 44. The sentence is
  restated per arm with those numbers.
- **A sign flips.** The coin-flip arm's selection lineage is energy-negative on 2 of the 3
  seeds (**−373 / −50 / +92**) while still gathering meals (44.3 / 45.2 / 45.5) — the sign of
  a random gate's final energy is not stable at this population size, and the coin arm and the
  lesion arm no longer rank against each other (coin below lesion on seed 11, above it on
  seeds 12 and 13).
- **What held on two seeds holds on three.** rewired > real brain > coin-flip by final mean
  energy on all three seeds (rewired 705 / 762 / 762, real brain 359 / 348 / 374, coin-flip
  −373 / −50 / 92), and the lesioned arm takes **0.0 meals** on all three seeds in both
  lineages. The rewired-over-real-brain comparison now runs against a real-brain lineage on
  its own seed every time.
- Table 6 (15 rows), Table 6b (12 rows) and Fig 7 (three curves per arm) carry the new seed;
  the Limitations device question now names the one cell that separates the seed effect from
  the device effect — the unmodified brain at seed 11, **366** on the cloud device against
  **359** on the original host, seed, population, world and code held fixed.

## What v6 added

The real-brain lineage is now measured on its own seed for both seeds, so the two-seed
claims compare like with like:

- `data/mac/ctrl/s12/ctrl_real_evolve_desire_{select,random}.json` — the unmodified brain,
  seed 12, on the cloud device: selection lineage ends at **348** mean energy (6/6 flies
  above zero, 47.5 meals), random control at **409** (6/6, 46.5 meals).
- `data/mac/ctrl/s11real/ctrl_real_evolve_desire_{select,random}.json` — the same brain at
  seed 11 on the cloud device: **366** (6/6, 47.5 meals) against the original host's **359**
  (6/6, 49.0 meals). Seed, population, world and code are held fixed, so that gap is the
  device effect at n=6 and it is the noise floor for every cross-device number in the paper.
  The ordering against the lesion arms survives it.
- `code/real_run.py` — the runner that produced both cells, with the environment it needs.
- The paper gained a References section naming the substrate sources with their DOIs, and
  Table 6, Table 6b and Fig 7 carry the new rows and curves.

## What was tested

A whole-organism connectome substrate — the MaleCNS v1.0 graph, **166,700 neurons carrying
a `superclass` annotation and 25,582,938 retained synapses** — wired into an LLM agent loop
as a fast, cheap front layer: it acts on tasks it has consolidated and escalates to the
model otherwise.

## Substrate provenance and attribution

The connectome is not our contribution; the measurements are. Stating that in the repo, not
only in the paper.

- **Source.** The **Janelia FlyEM male CNS connectome**, used through its public read-only
  snapshot `male-cns:v1.0` served by neuprint/DVID — the same release the
  [`natverse/malecns`](https://github.com/natverse/malecns) tooling wraps. Release page:
  <https://www.janelia.org/project-team/flyem/male-cns-connectome>. The files this project
  built from are `body-annotations-male-cns-v1.0-minconf-0.5.feather`,
  `body-neurotransmitters-male-cns-v1.0.feather` and
  `connectome-weights-male-cns-v1.0-minconf-0.5.feather`. The published release carries
  about 169,700 neurons.
- **Our build.** `code/build_graph.py` keeps only bodies carrying a `superclass` annotation,
  which yields **166,700 neurons and 25,582,938 retained synapses**. The neurotransmitter
  sign policy (acetylcholine +1, GABA/glutamate −1, everything else 0) and the edge-weight
  normalisation are stated assumptions of this project, written into the build script —
  properties of our graph, not of the source data.
- **Attribution obligation.** The release is CC BY (attribution required), so the substrate
  is cited wherever these numbers are quoted and any change we made to the graph is stated —
  which is what the bullet above does. The binding terms and the preferred citation live on
  the release page and in the accompanying paper's data-availability statement. Since v6 the
  paper carries a References section with the article DOI
  ([10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015)) and the release
  page is attached to the Zenodo record as a `Cites` related identifier. Check the terms
  before commercial reuse.
- **What is ours.** Wiring the substrate into an LLM agent loop, the gate measurement and
  its contrast readout, the token-cost accounting, the lesion controls, and the three roles
  the substrate was hoped to fill and did not.

## The claims, each with its number and its accounting

| Claim | Number | Accounting (which question it answers, the arm, the threshold) |
|---|---|---|
| The substrate buys a gate | 40–55 of 144 possible solo (zero-token) task executions per population per generation; best fly 8 of 18 tasks | App line, contrast readout (task rate = channel mean − rest-of-motor mean, threshold 0.01). `gpu_314` breaks out at generation 4; `gpu_313` at generation 217 |
| The solutions belong to the LLM, not the connectome | Held-out 24/24 solved, every solve by a fresh LLM generation (320–334 tokens each); a fly with 365 learned synapses on an essentially empty graph passed 180/180 checks | 8 flies × 3 never-trained tasks |
| The token bill is structural | 72 calls and ~47k tokens per generation, flat across 365 generations | Caused by cache eviction, independent of task difficulty |
| A per-fly policy governor cuts cost at zero meal loss | 116 → 57 LLM calls (−51%); paired w150 runs 58 → 24 (−59%) | Four paired runs, 24 paired fly-runs; governor meals equal baseline meals row for row |
| The economy gate is real | Satiety-gated feeding 8/8 survivals vs always-feeding 0/8 | 6 cells × 4 flies, upkeep 3e-4 |
| Closed-loop evolution works in the foraging world | 13/24 alive at generation 0 → 24/24 at generation 9 on two independent lineages (mean energy 6.7× and 5.8×); transfer to an unseen world seed 24/24 | 6 flies, 6 generations |
| Three candidate roles are dead, by measurement | Recursive memory horizon 1–2 steps; input relay equivalent to a linear copy (R² 0.91–0.96); zero channel margin under superposed cues (margin 0.0000) | 72-sample falsification of the decision-layer hypothesis (18 tasks × 4 amplitudes, 18 classes, chance 0.056) |
| Lesion controls, three seeds (final generation) | no-brain −231 / −151 / −72 E, meals **0.0 / 0.0 / 0.0**; rewired **+705 / +762 / +762**, 6/6, meals 72.8 / 75.7 / 76.0 (gate dead: mean D_gate 0.00 on all three, full-leak 1.00); coin-flip −373 / −50 / +92, meals 44.3 / 45.2 / 45.5; real brain +359 / +348 / +374, 6/6, meals 49.0 / 47.5 / 45.5 | Same economy and budget (upkeep 3e-4, meal 12), only the brain changes; 6 flies, 6 generations; seed 11 on CPU, seeds 12 and 13 on a cloud GPU under the same CUDA numerical path as the GPU host. The ordering rewired > real brain > coin-flip holds on all three; the coin arm and the lesion arm do not rank against each other |
| Selection is not the driver inside the control arms | the random control lineage flips the coin-flip arm's sign on two of three seeds (selected −373 / −50 / +92, random −131 / +111 / −74); the no-brain arm ends −231 / −151 / −72 selected and −136 / +1 / −177 random, all with zero meals | Table 6b: every arm also ran its random control (no selection, same economy) on all three seeds. Largest within-arm divergence 243 (coin), 152 (lesioned), 44 (rewired), against across-seed spreads of 465, 159 and 58 — on the coin arm the seed spread is the larger, which is the shape an arm with no structure to stabilise it should have. That bounds how much of Table 6 may be attributed to selection |

## Erratum found after the v3 deposit

The v3 text and abstract say **169,700** neurons. The artifact carries **166,700**
(`body_ids` length 166,700, `indptr` length 166,701). 169,700 is the MaleCNS v1.0 published
total; the difference is bodies without a `superclass` annotation, which the stated filter in
`code/build_graph.py` drops. The synapse count 25,582,938 is correct. Corrected in v4.

## Repository layout

- `code/` — the analysis scripts and the paper builder (stdlib + numpy/scipy/matplotlib/fpdf2
  only, no substrate imports) plus `build_graph.py`, which shows how the substrate graph was
  built from the published MaleCNS v1.0 flat-connectome files.
- `data/mac/` — ledgers from the Mac-run line: three app-line arms
  (`apps/harvest/<arm>/evo_ledger.jsonl`), the foraging lineages, and the control arms on
  three seeds (`ctrl/` seed 11, `ctrl/s12/` seed 12, `ctrl/s13/` seed 13, plus
  `ctrl/s11real/` — the seed-11 real brain re-run on the cloud device, the device-effect cell).
- `data/195/` — ledgers from the GPU host mirror: gate evolution, architecture ablation,
  economy gate, governor paired runs, teaching lineages.
- `paper/` — the deposited PDFs (English and Chinese). Regenerated figures land in
  `paper/figures/`.

## Reproducing the numbers

```bash
python3 -m venv .venv && .venv/bin/pip install numpy scipy matplotlib fpdf2
.venv/bin/python code/paper_draft_v7.py      # -> paper/figures/*.png and the PDF
```

Paths resolve relative to the repository, so no editing is needed. The Chinese edition
(`code/paper_draft_v7_zh.py`) exec's the English data section, so both languages carry
identical numbers; it needs the system CJK font `Arial Unicode.ttf`.

## What is deliberately not in this repository

- the substrate implementation (evolution kernel, agent loop, task battery) — the paper's
  claims are checkable from the ledgers without it;
- `malecns_graph.npz` (90 MB) and the per-fly checkpoints (127–150 MB each) — rebuild the
  graph with `code/build_graph.py` from the published MaleCNS v1.0 files;
- the app-line configuration ablations (19 arms) — under review;
- the per-fly solution stores (`*_store.json`) from the three harvested arms — no number in
  the paper is derived from them, and the generated solutions they carry quote a lab host on
  the local network. The ledgers the paper does read (`evo_ledger.jsonl`) ship byte-identical:
  no shipped ledger was edited on the way out.

## Scope, stated plainly

An empirical case study with negative results. Where a third seed has not run yet, the paper
says so — the control arms and the real-brain lineage are at three, the applied task line and
the GPU-host line are not. The three roles the substrate was hoped to fill — decision layer,
memory, input
relay — are each reported dead with their statistics. The headline is what a biological
substrate buys an LLM agent, what it does not buy, and what the whole arrangement costs.

## License

`code/` MIT; `paper/` CC BY 4.0, matching the Zenodo record.
