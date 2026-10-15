# A Drosophila connectome substrate inside an LLM agent

**Evidence package** for the preprint. Every figure and every table in `paper/` is
re-derivable from `data/` by `code/paper_draft_v5.py` (English) and
`code/paper_draft_v5_zh.py` (Chinese). The ledgers are shipped byte-identical to the ones
the paper read.

Preprint: **DOI [10.5281/zenodo.23397763](https://doi.org/10.5281/zenodo.23397763)**
(v4, published 2026-10-15, resource type Preprint, CC BY 4.0; a v5 draft with the random
control lineages is in `paper/`). All versions:
**DOI [10.5281/zenodo.23396755](https://doi.org/10.5281/zenodo.23396755)**.

> Luan, B. (2026). *A Drosophila connectome substrate inside an LLM agent: what it gates,
> what it does not, and what it costs* (Version v4). Zenodo.
> https://doi.org/10.5281/zenodo.23397763

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
  the release page and in the accompanying paper's data-availability statement; the exact
  article DOI is carried in the reference list of any derivative work and will be attached to
  the Zenodo record as a related identifier. Check the terms before commercial reuse.
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
| Lesion controls, two seeds (final generation) | no-brain −231 / −151 E, meals **0.0 / 0.0**; rewired **+705 / +762**, 6/6, meals 72.8 / 75.7 (gate dead: mean D_gate 0.00, full-leak 1.00); coin-flip −373 / −50, meals 44.3 / 45.2; real brain +359, 6/6, 49.0 | Same economy and budget (upkeep 3e-4, meal 12), only the brain changes; 6 flies, 6 generations; seed 11 on CPU, seed 12 on a cloud GPU under the 195 CUDA path |
| Selection is not the driver inside the control arms | the random control lineage flips the coin-flip arm's sign on seed 12 (−50 selected, **+111** random); the no-brain arm ends −151 selected and +0.5 random, both with zero meals | Table 6b: every arm also ran its random control (no selection, same economy) on both seeds. Inside an arm the two lineages disagree more than the two seeds do, which bounds how much of Table 6 may be attributed to selection |

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
  (`apps/harvest/<arm>/evo_ledger.jsonl`), the foraging lineages, the lesion controls (seed 11).
- `data/195/` — ledgers from the GPU host mirror: gate evolution, architecture ablation,
  economy gate, governor paired runs, teaching lineages.
- `paper/` — the deposited PDFs (English and Chinese). Regenerated figures land in
  `paper/figures/`.

## Reproducing the numbers

```bash
python3 -m venv .venv && .venv/bin/pip install numpy scipy matplotlib fpdf2
.venv/bin/python code/paper_draft_v5.py      # -> paper/figures/*.png and the PDF
```

Paths resolve relative to the repository, so no editing is needed. The Chinese edition
(`code/paper_draft_v5_zh.py`) exec's the English data section, so both languages carry
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

An empirical case study with negative results. Where a second seed has not run yet, the paper
says so. The three roles the substrate was hoped to fill — decision layer, memory, input
relay — are each reported dead with their statistics. The headline is what a biological
substrate buys an LLM agent, what it does not buy, and what the whole arrangement costs.

## License

`code/` MIT; `paper/` CC BY 4.0, matching the Zenodo record.
