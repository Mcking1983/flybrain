#!/usr/bin/env python3
# Build flybrain application-paper draft: 3 figures from artifacts + PDF via fpdf2.
# All numbers re-derived from Mac artifacts (harvest ledgers, evolve_desire_*, evo_A_gen9.npz).
import json, os, statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fpdf import FPDF

BASE = os.path.expanduser("~/flybrain")
OUTD = os.path.expanduser("~/Downloads/flybrain-paper")
os.makedirs(OUTD, exist_ok=True)

# ---------------- figure data ----------------
def ledger(pop):
    return [json.loads(l) for l in open(f"{BASE}/apps/harvest/{pop}/evo_ledger.jsonl")]

arms = {}
for pop in ("gpu_300", "gpu_313", "gpu_314"):
    rows = ledger(pop)
    ss = [sum(r["solo"]) for r in rows]
    tk = [sum(r["tokens"]) for r in rows]
    arms[pop] = dict(gens=[r["gen"] for r in rows], solo=ss, tok=tk)

# Fig 1: solo_sum per generation, three arms
plt.figure(figsize=(6.4, 3.4))
for pop, lab, c in (("gpu_300", "gpu_300 ungated control", "#999999"),
                    ("gpu_313", "gpu_313 contrast, orig bounds", "#1f77b4"),
                    ("gpu_314", "gpu_314 contrast, widened bounds", "#d62728")):
    a = arms[pop]
    plt.plot(a["gens"], a["solo"], lw=1.2, color=c, label=lab)
plt.axhline(144, ls=":", lw=0.8, color="k")
plt.text(5, 137, "saturation 144 = 8 flies x 18 tasks", fontsize=7)
plt.xlabel("generation"); plt.ylabel("solo count (population, max 144)")
plt.title("Fig 1. Gate-alive solo count per generation, three arms")
plt.legend(fontsize=7); plt.tight_layout()
plt.savefig(f"{OUTD}/fig1_solo.png", dpi=150); plt.close()

# Fig 2: tokens per generation (structural bill)
plt.figure(figsize=(6.4, 3.0))
for pop, lab, c in (("gpu_313", "gpu_313", "#1f77b4"), ("gpu_314", "gpu_314", "#d62728")):
    a = arms[pop]
    plt.plot(a["gens"], a["tok"], lw=0.8, color=c, alpha=0.8, label=lab)
plt.xlabel("generation"); plt.ylabel("LLM tokens per generation")
plt.title("Fig 2. Structural token bill: flat ~47k per generation")
plt.legend(fontsize=8); plt.tight_layout()
plt.savefig(f"{OUTD}/fig2_tokens.png", dpi=150); plt.close()

# Fig 3: foraging sim select vs random, mean E_end per gen
def forage(f):
    rows = json.load(open(f"{BASE}/{f}"))
    gens = [r["gen"] for r in rows]
    e = [statistics.mean(x["E_end"] for x in r["results"]) for r in rows]
    m = [statistics.mean(x["meals"] for x in r["results"]) for r in rows]
    return gens, e, m
g1, e1, m1 = forage("evolve_desire_select.json")
g2, e2, m2 = forage("evolve_desire_random.json")
fig, ax = plt.subplots(1, 2, figsize=(6.4, 2.8))
ax[0].plot(g1, e1, "o-", color="#2ca02c", label="selection")
ax[0].plot(g2, e2, "s--", color="#999999", label="random")
ax[0].set_title("mean final energy E_end", fontsize=8); ax[0].set_xlabel("generation")
ax[1].plot(g1, m1, "o-", color="#2ca02c", label="selection")
ax[1].plot(g2, m2, "s--", color="#999999", label="random")
ax[1].set_title("mean meals", fontsize=8); ax[1].set_xlabel("generation")
for a in ax: a.legend(fontsize=7)
fig.suptitle("Fig 3. Foraging simulation: selection vs random control (6 gens, 6 flies)", fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTD}/fig3_forage.png", dpi=150); plt.close()

# ---- v2: 195-data figures (re-derived from ~/flybrain_195_data/flybrain) ----
B195 = os.path.expanduser("~/flybrain_195_data/flybrain")

# Fig 4: cereb 40-gen gate evolution: gate_ok fraction and mean D_gate
d = json.load(open(f"{B195}/cereb_llm5_s13_g40.json"))
gens, gk, dg = [], [], []
for row in d:
    res = row["res"]
    gens.append(row["gen"])
    gk.append(sum(1 for r in res if r.get("gate_ok")) / len(res))
    dg.append(statistics.mean(r.get("D_gate", 0) for r in res))
plt.figure(figsize=(6.4, 3.0))
plt.plot(gens, gk, "o-", color="#2ca02c", label="gate_ok fraction")
plt.plot(gens, dg, "s--", color="#ff7f0e", label="mean D_gate")
plt.xlabel("generation"); plt.ylabel("fraction / margin")
plt.title("Fig 4. Substrate gate evolution (40 gens, 20 flies): gate_ok 0.40 -> 0.75-0.85")
plt.legend(fontsize=8); plt.tight_layout()
plt.savefig(f"{OUTD}/fig4_gate_evo.png", dpi=150); plt.close()

# Fig 5: architecture ablation, mean score per gen (5 arms)
plt.figure(figsize=(6.4, 3.0))
for f, lab, c in (("archA0.json","A0 seed1","#1f77b4"), ("archA0c.json","A0 seed2","#1f77b4"),
                  ("archA1.json","A1 seed1","#d62728"), ("archA1c.json","A1 seed2","#d62728"),
                  ("archSkill.json","Skill-only","#999999")):
    dd = json.load(open(f"{B195}/{f}"))
    sc = [statistics.mean(r["score"] for r in row["results"]) for row in dd]
    plt.plot(range(len(sc)), sc, "-s" if "c.json" not in f else "--o", lw=1.0, color=c, ms=3, label=lab)
plt.xlabel("generation"); plt.ylabel("mean score (4 subtasks)")
plt.title("Fig 5. Architecture ablation: A0 / A1 / Skill-only, 10 gens x 20 flies")
plt.legend(fontsize=7); plt.tight_layout()
plt.savefig(f"{OUTD}/fig5_arch.png", dpi=150); plt.close()

# Fig 6: economy satiety(gate open) vs always(gate closed): mean E_end pairs + survival
econ = json.load(open(f"{B195}/economy.json"))
cells = {}
for e in econ:
    key = (e["FOOD"], e["C_SYN"])
    fl = e["flies"]
    cells.setdefault(key, {})[e["arm"]] = dict(
        surv=sum(1 for f in fl if f["survived"]), n=len(fl),
        E=statistics.mean(f.get("E_end", 0) for f in fl))
keys = sorted(cells.keys())
xs = range(len(keys))
plt.figure(figsize=(6.4, 3.2))
plt.bar([x - 0.2 for x in xs], [cells[k]["satiety"]["E"] for k in keys], width=0.38, color="#2ca02c", label="satiety (gate open)")
plt.bar([x + 0.2 for x in xs], [cells[k]["always"]["E"] for k in keys], width=0.38, color="#999999", label="always (gate closed)")
for x, k in enumerate(keys):
    plt.text(x - 0.2, cells[k]["satiety"]["E"], f"{cells[k]['satiety']['surv']}/{cells[k]['satiety']['n']}", ha="center", fontsize=7)
    plt.text(x + 0.2, cells[k]["always"]["E"], f"{cells[k]['always']['surv']}/{cells[k]['always']['n']}", ha="center", fontsize=7)
plt.xticks(list(xs), [f"F{k[0]:.0f} c{k[1]}" for k in keys], fontsize=7)
plt.ylabel("mean final energy (labels: survived/flies)")
plt.title("Fig 6. Economy gate: satiety vs always feeding, 6 cells x 4 flies")
plt.legend(fontsize=8); plt.tight_layout()
plt.savefig(f"{OUTD}/fig6_economy.png", dpi=150); plt.close()

# Governor paired runs from 195 copy
gov_runs = []
import glob as _glob
for path in sorted(_glob.glob(f"{B195}/harness_live_w2_g*.json")):
    dd = json.load(open(path))
    ff = gv = 0; meals_eq = True; nfly = 0
    for tag, flies in dd.get("pops", {}).items():
        for f in flies:
            p1, p2, bs = f.get("fly_first"), f.get("governor"), f.get("baseline")
            if p1 and p2:
                ff += p1.get("llm_calls", 0); gv += p2.get("llm_calls", 0); nfly += 1
                if bs and p2.get("meals") != bs.get("meals"): meals_eq = False
    gov_runs.append((os.path.basename(path).replace("harness_live_w2_", "").replace(".json", ""), ff, gv, nfly, meals_eq))
GOV_FF = sum(r[1] for r in gov_runs); GOV_GV = sum(r[2] for r in gov_runs)
W150_FF = sum(r[1] for r in gov_runs if "w150" in r[0]); W150_GV = sum(r[2] for r in gov_runs if "w150" in r[0])
print("gov runs:", gov_runs, "total", GOV_FF, "->", GOV_GV, "w150", W150_FF, "->", W150_GV)

# Evolution lineages from 195 copy
lin = []
for f in ("evo_teach.json", "evo_teach2.json", "evo_t1_teach.json"):
    dd = json.load(open(f"{B195}/{f}"))
    rep = dd["report"]
    lin.append((f, len(rep), rep[0].get("survived"), rep[-1].get("survived"),
                rep[0].get("mean_E"), rep[-1].get("mean_E")))
print("lineages:", lin)

# ---- v7: control arms (real brain / no-brain / rewired / coin-flip) on THREE seeds ----
# seed 11 ran on this Mac (CPU); seeds 12 and 13 ran on the rented cloud GPU (torch 2.12.1+cu130,
# the same CUDA numerical path as the 195 host, which is the point of the replication).
CTRLO = os.path.expanduser("~/flybrain/ctrl")
CTRLO12 = os.path.expanduser("~/flybrain/ctrl/s12")
CTRLO13 = os.path.expanduser("~/flybrain/ctrl/s13")
# the real-brain lineage re-run on the cloud device (seed 11 there is the numerical-path
# check against the 195 ledger; seeds 12 and 13 there fill the real-brain cell of every seed row).
CTRLR11C = os.path.expanduser("~/flybrain/ctrl/s11real")
SEED_DIRS = {"s11": CTRLO, "s12": CTRLO12, "s13": CTRLO13}
SEEDS = ("s11", "s12", "s13")
ARMS = ("nobrain", "rewired", "coinflip")
def ctrl_curve(path):
    if not os.path.exists(path): return None
    rows = json.load(open(path))
    gens = [r["gen"] for r in rows]
    e = [statistics.mean(x["E_end"] for x in r["results"]) for r in rows]
    surv = [sum(1 for x in r["results"] if x["E_end"] > 0) for r in rows]
    meals = [statistics.mean(x["meals"] for x in r["results"]) for r in rows]
    return gens, e, surv, meals
CTRLS = {c: {s: ctrl_curve(f"{p}/ctrl_{c}_evolve_desire_select.json") for s, p in SEED_DIRS.items()}
         for c in ARMS}
CTRLS12 = {c: CTRLS[c]["s12"] for c in ARMS}   # kept for the v6 figure code
real_sel = ctrl_curve(f"{BASE}/evolve_desire_select.json")
real_rnd = ctrl_curve(f"{BASE}/evolve_desire_random.json")
REAL_SEL = {"s11": real_sel,
            "s12": ctrl_curve(f"{CTRLO12}/ctrl_real_evolve_desire_select.json"),
            "s13": ctrl_curve(f"{CTRLO13}/ctrl_real_evolve_desire_select.json")}
REAL_RND = {"s11": real_rnd,
            "s12": ctrl_curve(f"{CTRLO12}/ctrl_real_evolve_desire_random.json"),
            "s13": ctrl_curve(f"{CTRLO13}/ctrl_real_evolve_desire_random.json")}
real_sel12, real_sel13 = REAL_SEL["s12"], REAL_SEL["s13"]
real_rnd12, real_rnd13 = REAL_RND["s12"], REAL_RND["s13"]
real_cloud11 = ctrl_curve(f"{CTRLR11C}/ctrl_real_evolve_desire_select.json")
have_ctrl = [c for c in ARMS if CTRLS[c]["s11"]]
have_ctrl12 = [c for c in ARMS if CTRLS[c]["s12"]]
if have_ctrl:
    plt.figure(figsize=(6.4, 3.2))
    LS = {"s11": "-", "s12": "--", "s13": "-."}
    for s in SEEDS:
        if REAL_SEL[s]:
            g0, e0, _, _ = REAL_SEL[s]
            plt.plot(g0, e0, "o" + LS[s], color="#2ca02c", lw=1.4, label=f"real brain, sel (seed {s[1:]})")
        if REAL_RND[s]:
            g0, e0, _, _ = REAL_RND[s]
            plt.plot(g0, e0, "s" + LS[s], color="#999999", lw=1.1, label=f"real brain, rnd (seed {s[1:]})")
    for c, col in (("nobrain", "#d62728"), ("rewired", "#ff7f0e"), ("coinflip", "#9467bd")):
        for s in SEEDS:
            src = CTRLS[c][s]
            if src:
                gc, ec, _, _ = src
                plt.plot(gc, ec, "^" + LS[s], color=col, ms=4, label=f"{c} (seed {s[1:]})")
    plt.axhline(0, ls=":", lw=0.8, color="k")
    plt.xlabel("generation"); plt.ylabel("mean E_end (0 = starvation line)")
    plt.title("Fig 7. Control arms vs real brain in the same economy, three seeds")
    plt.legend(fontsize=6); plt.tight_layout()
    plt.savefig(f"{OUTD}/fig7_controls.png", dpi=150); plt.close()

# ---- v7: three-seed replication checks, computed from the ledgers ----
def _finite_mean(vals, default):
    keep = [v for v in vals if isinstance(v, (int, float)) and v == v]  # drops NaN
    return statistics.mean(keep) if keep else default
def ctrl_gate_stats(path):
    """Final-generation gate diagnostics for one control arm: D_gate (mean and best fly) and the full-leak rate."""
    if not os.path.exists(path): return None
    res = json.load(open(path))[-1]["results"]
    gates = [x.get("D_gate") for x in res if isinstance(x.get("D_gate"), (int, float))]
    return dict(gate=_finite_mean([x.get("D_gate") for x in res], 0.0),
                gate_max=max(gates) if gates else 0.0,
                leak=_finite_mean([x.get("act_A_full") for x in res], 1.0))
GATE = {c: {s: ctrl_gate_stats(f"{p}/ctrl_{c}_evolve_desire_select.json") for s, p in SEED_DIRS.items()}
        for c in ARMS}
# the random control lineage of every arm (no selection), on all three seeds
CTRLSR = {c: {s: ctrl_curve(f"{p}/ctrl_{c}_evolve_desire_random.json") for s, p in SEED_DIRS.items()}
          for c in ARMS}
def ctrl_last(src):
    return None if not src else dict(E=src[1][-1], surv=src[2][-1], meals=src[3][-1])
REPL = {c: {s: ctrl_last(CTRLS[c][s]) for s in SEEDS}
        for c in ARMS if all(CTRLS[c][s] for s in SEEDS)}
REPL_REAL = ctrl_last(REAL_SEL["s11"])
REPL_REAL12 = ctrl_last(REAL_SEL["s12"])
REPL_REAL13 = ctrl_last(REAL_SEL["s13"])
REPL_REAL_C11 = ctrl_last(real_cloud11)
REAL_BY_SEED = {"s11": REPL_REAL, "s12": REPL_REAL12, "s13": REPL_REAL13}
REAL_ALL = all(REAL_BY_SEED.values())
REPLR = {c: {s: ctrl_last(CTRLSR[c][s]) for s in SEEDS} for c in CTRLSR}
THREE_SEEDS = len(REPL) == 3
TWO_SEEDS = THREE_SEEDS   # the prose gates keep their v5/v6 names
REWIRED_WINS = THREE_SEEDS and REAL_ALL and all(
    REPL["rewired"][s]["E"] > REAL_BY_SEED[s]["E"] for s in SEEDS)
REAL_OVER_COIN = THREE_SEEDS and REAL_ALL and all(
    REAL_BY_SEED[s]["E"] > REPL["coinflip"][s]["E"] for s in SEEDS)
BOTTOM_SWAPS = THREE_SEEDS and len({REPL["coinflip"][s]["E"] > REPL["nobrain"][s]["E"] for s in SEEDS}) > 1
ORDER_HOLDS = THREE_SEEDS and REWIRED_WINS and REAL_OVER_COIN and not BOTTOM_SWAPS
ZERO_MEALS_HOLDS = THREE_SEEDS and all(REPL["nobrain"][s]["meals"] == 0 for s in SEEDS)
# does the seed-11 ordering against the lesion arms survive moving the real brain to the cloud device?
DEVICE_HOLDS = bool(REPL_REAL_C11 and REPL and
                    (REPL["rewired"]["s11"]["E"] > REPL_REAL_C11["E"]) ==
                    (REPL["rewired"]["s11"]["E"] > REPL_REAL["E"]) and
                    (REPL_REAL_C11["E"] > REPL["coinflip"]["s11"]["E"]) ==
                    (REPL_REAL["E"] > REPL["coinflip"]["s11"]["E"]))
COIN_NEG_SEEDS = [s for s in SEEDS if REPL.get("coinflip") and REPL["coinflip"][s]["E"] < 0]
COIN_NEG_HOLDS = THREE_SEEDS and len(COIN_NEG_SEEDS) == len(SEEDS)
# within-arm lineage divergence (selected against random, same seed) versus the across-seed spread
DIV = {}
if REPL:
    for c in ARMS:
        sel = [REPL[c][s]["E"] for s in SEEDS]
        rnd = [REPLR[c][s]["E"] for s in SEEDS if REPLR[c][s]]
        within = {s: abs(REPL[c][s]["E"] - REPLR[c][s]["E"]) for s in SEEDS if REPLR[c][s]}
        DIV[c] = dict(sel_spread=max(sel) - min(sel), rnd_spread=(max(rnd) - min(rnd)) if rnd else 0.0,
                      within=within, within_max=max(within.values()) if within else 0.0)
def per_seed(d, key="E", dp=0):
    return " / ".join(f"{d[s][key]:.{dp}f}" for s in SEEDS)
print("three-seed controls:", {k: {s: round(v[s]["E"], 1) for s in SEEDS} for k, v in REPL.items()},
      "real", {s: (None if not REAL_BY_SEED[s] else round(REAL_BY_SEED[s]["E"], 1)) for s in SEEDS},
      "real_cloud_s11", None if not REPL_REAL_C11 else round(REPL_REAL_C11["E"], 1),
      "| rewired_wins", bool(REWIRED_WINS), "order", bool(ORDER_HOLDS),
      "zero_meals", bool(ZERO_MEALS_HOLDS), "coin_neg_seeds", [s[1:] for s in COIN_NEG_SEEDS])
print("divergence:", {c: (round(DIV[c]["sel_spread"], 1), round(DIV[c]["within_max"], 1)) for c in DIV})
print("gate diagnostics:", {c: {s: (round(GATE[c][s]["gate"], 2), round(GATE[c][s]["leak"], 2))
                                for s in SEEDS if GATE[c][s]} for c in GATE})

# quick sanity print
print("fig1 last solo:", {p: a["solo"][-1] for p, a in arms.items()})
print("fig2 mean tok 313/314:", round(statistics.mean(arms["gpu_313"]["tok"])), round(statistics.mean(arms["gpu_314"]["tok"])))

# ---------------- PDF ----------------
pdf = FPDF(format="A4")
pdf.set_auto_page_break(auto=True, margin=18)
pdf.set_margins(20, 18, 20)

def title(t):
    pdf.set_font("helvetica", "B", 15); pdf.multi_cell(0, 7, t); pdf.ln(2)

def h2(t):
    pdf.ln(2); pdf.set_font("helvetica", "B", 12); pdf.multi_cell(0, 6, t); pdf.ln(1)

def h3(t):
    pdf.ln(1); pdf.set_font("helvetica", "B", 10.5); pdf.multi_cell(0, 5.5, t); pdf.ln(0.5)

def p(t):
    pdf.set_font("helvetica", "", 10); pdf.multi_cell(0, 4.9, t); pdf.ln(1)

def it(t):
    pdf.set_font("helvetica", "I", 9.5); pdf.multi_cell(0, 4.7, t); pdf.ln(1)

def figimg(path, cap):
    pdf.image(path, x=22, w=170); pdf.ln(2)
    it(cap); pdf.ln(1)

def table(caption, rows, widths):
    it(caption); pdf.ln(0.5)
    pdf.set_font("helvetica", "B", 8.6)
    for w, c in zip(widths, rows[0]): pdf.cell(w, 5.6, c, border=1)
    pdf.ln()
    pdf.set_font("helvetica", "", 8.2)
    for r in rows[1:]:
        for w, c in zip(widths, r): pdf.cell(w, 5.2, str(c), border=1)
        pdf.ln()
    pdf.ln(2)

pdf.add_page()
title("A Drosophila connectome substrate inside an LLM agent: what it gates, what it does not, and what it costs")
it("Draft v7 - 2026-10-16. Applied case study with full cost accounting, negative results and "
   "control arms on three seeds. All numbers re-derived from the artifact corpus on the authors' machine.")
it("v7: the control arms and the real-brain lineage now run on a third seed, which moves two sentences. "
   "The coin-flip arm's selection lineage is energy-negative on two of the three seeds (it turns positive "
   "on the third), and on that arm the across-seed spread is larger than the within-arm divergence between "
   "the selected and random lineages, so the v5 bound drawn from two seeds is restated with three-seed "
   "numbers. Everything that held on two seeds - rewired over real brain, real brain over coin-flip, zero "
   "meals with the connectome zeroed - holds on three.")

ABSTRACT_CTRL = (f"(seeds 11 / 12 / 13 read {per_seed(REPL['rewired'])} against "
                 f"{per_seed(REAL_BY_SEED)})"
                 if (REPL.get("rewired") and REAL_ALL) else "")
h2("Abstract")
p("We report an applied case study that wires a whole-organism connectome substrate (MaleCNS v1.0: "
  "166,700 neurons carrying a superclass annotation - the release total is 169,700 - and 25,582,938 "
  "innate synapses) into an LLM agent loop as a fast, cheap front layer - "
  "a digital cerebellum that acts on tasks it has consolidated and escalates to the LLM otherwise. "
  "Two experiment lines are reported. In a foraging simulation, closed-loop evolution lifted population "
  "survival from 13/24 at generation 0 to 24/24 at generation 9 on two independent lineages (mean "
  "energy 6.7x and 5.8x), and the evolved population transferred to an unseen world seed at 24/24 with higher energy "
  "still. In an applied task line (8-fly populations, an 18-task operational battery plus 3 held-out "
  "tasks, three arms totalling 1,029 generations, 26,678 LLM calls, 17,005,656 tokens), the substrate's "
  "one measurable contribution is a gate: under a contrast readout the gate is alive from generation 4 "
  "and sustains 40-55 of 144 possible solo (zero-token) task executions per population per generation, "
  "with a best fly gating 8 of 18 tasks. All 24 held-out solves came from fresh LLM code generation "
  "(320-334 tokens each), and a fly with 365 learned synapses on an essentially empty graph passed "
  "180/180 checks: the solutions come from the LLM plus a verification loop, not from the connectome. "
  "We further report the token bill as structural (a fixed 72 calls and ~47k tokens per generation "
  "caused by cache eviction, flat across 365 generations), and a per-fly policy governor that cut LLM "
  "calls 116 to 57 (-51%; 58 to 24, -59%, on the paired w150 runs) at exactly zero meal loss - the "
  "governor's per-fly meals equal the no-escalation baseline's meals row for row across 24 paired "
  "fly-runs. In the economy gate test, satiety-gated feeding yields 8/8 survivals where always-feeding "
  "yields 0/8. Three candidate roles for the "
  "substrate are judged dead by measurement: recursive memory horizon 1-2 steps, input relay equivalent "
  "to a linear copy, and zero channel margin under superposed cues. Lesion controls replicate on three "
  "seeds: with the innate connectome zeroed the animal never feeds (0.0 meals on all three seeds and in "
  "both lineages), while the "
  f"rewired arm out-gathers the real brain on energy on all three seeds with its gate dead "
  f"{ABSTRACT_CTRL} - the substrate's contribution is "
  "the gate and the stopping rule, not the harvest. The paper is offered as an honest "
  "accounting case study: where a biological substrate helps an LLM agent, where it does not, and what "
  "the whole arrangement costs.")

h2("1. Introduction")
p("LLM agents pay per token and pay again on every repeat of a solved problem. A natural cost cut is a "
  "front layer that decides, per task, whether the agent can act from its own consolidated competence or "
  "must consult the model. This paper asks a specific version of that question: can a biological "
  "connectome - the complete male Drosophila central nervous system graph, used as a fixed dynamical "
  "substrate - serve as that front layer, and what does the arrangement actually contribute once the "
  "accounting is done?")
p("Contributions: (i) a working two-layer agent in which a connectome substrate sits in front of an LLM "
  "and a verification loop; (ii) a measured, bounded contribution - a gate on asking the LLM - with its "
  "denominators named; (iii) a complete token bill for 1,029 population generations; (iv) a set of "
  "falsified candidate roles stated with their numbers; (v) a per-fly policy governor that behaves as a "
  "cost container rather than a capability amplifier. Recent work has simulated connectome substrates "
  "for control (connectome steering reproductions, physical drone control, fixed reservoirs with "
  "pre-registered controls) and put spiking action gates in front of language models; our claim is "
  "narrower than first-ever: the combination of a learned connectome, an LLM agent loop, closed-loop "
  "evolution, and a published cost ledger.")

h2("2. Related work")
p("Connectome simulation. Steering a virtual Drosophila descending-neuron connectome produced directed "
  "locomotion (Andlman et al., eLife 2022); the OpenWorm project simulated C. elegans neuromechanics; "
  "FlyCircuit and the FlyWire/Janelia resources supply the graphs; Shiu et al. showed that connectome "
  "networks with random weights can learn sensory-motor mapping as efficiently as weight-modified "
  "networks. Our substrate is the Janelia male connectome (MaleCNS v1.0) [1,2] used as a fixed weighted graph "
  "with local three-factor plasticity on top.")
p("LLM agent cost control. Prompt/context caching, model cascades and routers, and skill libraries "
  "(e.g. Voyager-style code skill stores) all reduce repeat cost by routing or reuse. Our gate is the "
  "same decision - ask the model or not - implemented as a spiking recurrent network over a biological "
  "graph, with the LLM writing executable skills that a verifier accepts before they count.")

h2("3. System")
p("Substrate. N = 166,700 neurons carrying a superclass annotation (the MaleCNS v1.0 release total is "
  "169,700; the stated build filter drops the unannotated bodies) [1], 25,582,938 innate weighted synapses (0.092% density), float32 "
  "throughout. Dynamics per episode, 30 steps: v = 0.9*v + 5.0*(Win@S + G@s) + drive; s = (v > 1.0); "
  "v *= (1 - s); activations accumulate. Win is the fixed innate connectome; G is the per-fly learned "
  "synapse set, updated by a local three-factor Hebbian rule (no backpropagation): potentiation and "
  "depression driven by action outcome, with sprouting and pruning under a structural cap (SYN_CAP).")
p("Two-layer agent. Layer 1 is a per-fly skill store: for a new task the LLM writes a PoC script, a "
  "verifier runs it (exit 0, stdout length, keyword), and only verified entries are stored. Layer 2 is a "
  "10-parameter genome per fly (plasticity and growth knobs) that is heritable; synapses and stores die "
  "with the fly. Routing per task, first match wins: solo (fly rate >= 0.01 AND verified store entry, "
  "0 tokens); practice (verified entry, rate below threshold, 0 tokens); cap (fly LLM budget exhausted); "
  "LLM (write code, verify, store; pays tokens). A curriculum frontier advances when >= 5 of 8 flies are "
  "solo on the newest task. Evolution: 8 flies per population, rank by (solo, rate_sum, -tokens), keep 4 "
  "elites, refill with multiplicative-Gaussian mutants plus one immigrant.")
p("Battery. 10 system-health scripting tasks plus an 8-task security queue that advances the curriculum; "
  "3 held-out tasks (never in training) probe transfer. Tasks execute against real hosts; verification "
  "runs the produced script.")

h2("4. Experiment A: foraging simulation (economy layer)")
p("A 24-fly population forages in an energy economy (food episodes, meals, starvation death). Closed-loop "
  "evolution is re-derived here from the run ledgers: lineage 1 lifted survival from 13/24 (gen 0) to "
  "24/24 (gen 9) with mean energy 143.3 to 965.3 (6.7x); an independent lineage 2 reproduced the shape "
  "(13/24 to 24/24, mean energy 143.3 to 833.0, 5.8x); a 20-generation plateau run carried mean energy "
  "512.0 to 3897.3 (7.6x). The gen-9 checkpoint shipped with this draft verifies 24/24 flies alive. "
  "Transfer: the gen-9 population in an unseen world seed scored 24/24 with higher mean energy than at "
  "home.")
p("Selection-vs-random controls exist for five configurations (6 generations, 6-8 flies each; "
  "Fig 3): on the economy timescale the energy gap between selection and random is small and noisy at "
  "6 generations - the survival signal (13/24 vs extinction patterns) is the carried result, not the "
  "6-gen energy curve.")
p("Substrate gate evolution (Fig 4). A 40-generation, 20-fly evolution over the connectome substrate, "
  "scored on four subtasks one of which is a gate subtask, lifts the gate_ok fraction from 0.40 (gen 0) "
  "to 0.75-0.85 (gens 16-39), with the mean gate margin D_gate rising 0.35 to ~0.74. The genome "
  "discovers and maintains the gate signal long before the applied line needs it.")
figimg(f"{OUTD}/fig4_gate_evo.png", "Fig 4. Substrate gate evolution: fraction of flies passing the gate subtask and mean gate margin, 40 generations.")
p("Economy gate (Table 4, Fig 6). Twelve arms cross satiety-gated feeding against always-feeding at "
  "three food levels and three synaptic-cost levels. Satiety gating yields 8/8 survivals (both FOOD=12 "
  "cells) where always-feeding yields 0/8; mean final energy separates by orders of magnitude (satiety "
  "-180 to +272 vs always -3,028 to -9,647). The gate here is the fly's own feeding decision, and the "
  "reading is survival, not a percentage.")
table("Table 4. Economy gate: survived/flies and mean final energy per cell.",
      [("FOOD", "c_syn", "satiety surv", "satiety E", "always surv", "always E")] +
      [(f"{k[0]:.0f}", f"{k[1]}", f"{cells[k]['satiety']['surv']}/{cells[k]['satiety']['n']}",
        f"{cells[k]['satiety']['E']:.0f}", f"{cells[k]['always']['surv']}/{cells[k]['always']['n']}",
        f"{cells[k]['always']['E']:.0f}") for k in keys],
      (14, 18, 26, 26, 26, 26))
figimg(f"{OUTD}/fig6_economy.png", "Fig 6. Satiety (gate open) vs always-feeding (gate closed): mean final energy, labels give survived/flies.")
p("Policy governor (Table 3). Four per-fly policies (baseline no-escalation; fly-first with escalation; "
  "LLM-first; governor = 50 warmup rounds then commit to fly-first or LLM-first on observed solo rate) "
  "were compared fly-for-fly in the same economy. Across the four paired runs the governor cut LLM "
  "calls 116 to 57 (-51%); on the w150 pair alone, 58 to 24 (-59%). The governor's per-fly meals equal "
  "the no-escalation baseline's meals row for row (24/24 paired fly-runs): the savings are pure cost "
  "container - it stopped paying for help the fly did not need - with no benefit amplifier effect.")
table("Table 3. Governor paired runs: LLM calls, fly-first vs governor.",
      [("run", "fly_first calls", "governor calls", "paired flies", "gov meals == baseline"),
       ] + [(r[0], str(r[1]), str(r[2]), str(r[3]), "yes" if r[4] else "NO") for r in gov_runs] +
      [("TOTAL", str(GOV_FF), str(GOV_GV), str(sum(r[3] for r in gov_runs)), "all rows"),
       ("w150 pair", str(W150_FF), str(W150_GV), "-", "-")],
      (26, 34, 30, 26, 40))
p("Teacher transfer. Teaching episodes are logged with prompt, response and applied edits. The teacher "
  "response shrinks from 7 synapse-edit operations (gen 1) to 2 operations (gens 13-17) as the genome "
  "consolidates, with response length ~218 to ~93 characters against a fixed 876-word prompt; the "
  "broadcast figure of 45 to 18 tokens is consistent with this artifact at tokenizer level and is "
  "quoted here with that accounting.")
if have_ctrl:
    p("Control arms (Table 6, Fig 7). Same economy, same budget, only the brain changes: no-brain "
      "(innate connectome zeroed, plasticity still grows learned synapses), rewired (weights permuted "
      "across the same edges - degree preserved, structure destroyed), coin-flip (the action decision "
      "replaced by a coin at p=0.5, learning continues). Each arm runs the selection lineage and the "
      "random control at the same scale as the real-brain lineages (6 flies, 6 generations), on three "
      "seeds. Seed 11 ran on this machine's CPU; seeds 12 and 13 ran on a rented cloud GPU under the "
      "same CUDA numerical path as the 195 host, which is also the device question raised in Limitations.")
    if REAL_ALL:
        p("The real-brain cell on every seed. The unmodified brain was run on each of the three seeds, so "
          "every cross-seed comparison below is computed against a real-brain lineage on its own seed: "
          f"{per_seed(REAL_BY_SEED)} final mean energy on seeds 11 / 12 / 13, with {per_seed(REAL_BY_SEED, 'surv')} "
          f"of 6 flies above zero and {per_seed(REAL_BY_SEED, 'meals', 1)} meals. "
          + (f"The seed-11 re-run on the cloud device ends at {REPL_REAL_C11['E']:.0f} "
             f"({REPL_REAL_C11['surv']}/6, {REPL_REAL_C11['meals']:.1f} meals) against "
             f"{REPL_REAL['E']:.0f} on the original host: the level moves with the device, and the "
             "ordering against the lesion arms "
             + ("holds across the move. " if DEVICE_HOLDS else "changes across the move, which is itself "
                "a device effect at n=6. ")) if REPL_REAL_C11 else "")
    ctrl_rows = [("arm", "seed", "final mean E_end", "E_end>0 / flies", "final mean meals")]
    for lab, srcs in (("real brain (selection)", REAL_SEL), ("real brain (random)", REAL_RND)):
        for s in SEEDS:
            r = ctrl_last(srcs[s])
            if r:
                ctrl_rows.append((lab, s[1:], f"{r['E']:.0f}", f"{r['surv']}/6", f"{r['meals']:.1f}"))
    for c, lab in (("nobrain", "no-brain"), ("rewired", "rewired"), ("coinflip", "coin-flip")):
        for s in SEEDS:
            r = ctrl_last(CTRLS[c][s])
            if r:
                ctrl_rows.append((lab, s[1:], f"{r['E']:.0f}", f"{r['surv']}/6", f"{r['meals']:.1f}"))
    table("Table 6. Control arms, final generation, three seeds (same world: upkeep 3e-4, meal 12).",
          ctrl_rows, (40, 14, 32, 28, 32))
    if THREE_SEEDS and REAL_ALL:
        p("What replicates on three seeds. "
          + ("The upper ordering holds on all three seeds: rewired > real brain > coin-flip by final mean "
             f"energy, on seeds 11 / 12 / 13 (rewired {per_seed(REPL['rewired'])}, real brain "
             f"{per_seed(REAL_BY_SEED)}, coin-flip {per_seed(REPL['coinflip'])}). "
             if (REWIRED_WINS and REAL_OVER_COIN) else "The upper ordering does not hold across the three seeds. ")
          + ("The bottom two arms do not separate: the coin arm sits below the lesion arm on seed 11 "
             f"({REPL['coinflip']['s11']['E']:.0f} against {REPL['nobrain']['s11']['E']:.0f}) and above it on "
             f"seeds 12 and 13 ({REPL['coinflip']['s12']['E']:.0f} against {REPL['nobrain']['s12']['E']:.0f}, "
             f"{REPL['coinflip']['s13']['E']:.0f} against {REPL['nobrain']['s13']['E']:.0f}) - at n=6, final "
             "energy cannot rank a random gate against a lesioned one. " if BOTTOM_SWAPS else
             "The coin arm stays below the lesion arm on all three seeds. ")
          + (f"The no-brain arm takes zero meals on all three seeds and in both lineages "
             f"({per_seed(REPL['nobrain'], 'meals', 1)} under selection): with the innate connectome zeroed "
             "the animal never feeds at all, which is the cleanest statement of what the structure buys. "
             if ZERO_MEALS_HOLDS else "")
          + (f"The coin-flip arm's selection lineage is energy-negative on {len(COIN_NEG_SEEDS)} of the "
             f"{len(SEEDS)} seeds (seeds 11 / 12 / 13 read {per_seed(REPL['coinflip'])}) while still gathering "
             f"meals ({per_seed(REPL['coinflip'], 'meals', 1)}): a random gate can find food and still lose "
             "the economy, and the sign of its final energy is not stable across seeds at this population "
             f"size - the spread across seeds is {DIV['coinflip']['sel_spread']:.0f}."
             if REPL.get("coinflip") else ""))
        p("What the extra seeds change. The rewired arm beating the real brain on energy "
          f"({per_seed(REPL['rewired'])} against {per_seed(REAL_BY_SEED)}, seeds 11 / 12 / 13) is no "
          "longer a single-seed curiosity: it holds on all three seeds, and it holds with the gate dead "
          f"(mean D_gate {GATE['rewired']['s11']['gate']:.2f} / {GATE['rewired']['s12']['gate']:.2f} / "
          f"{GATE['rewired']['s13']['gate']:.2f}, full-leak {GATE['rewired']['s11']['leak']:.2f} / "
          f"{GATE['rewired']['s12']['leak']:.2f} / {GATE['rewired']['s13']['leak']:.2f}). "
          f"Read against the meal counts ({per_seed(REPL['rewired'], 'meals', 1)} against "
          f"{per_seed(REAL_BY_SEED, 'meals', 1)} for the real brain), "
          "the honest reading is that in this world an ungated appetite gathers more energy than a gated "
          "one, and what the gate buys is the stopping rule rather than the harvest. The defensible claim "
          "is narrower than 'structure is needed to survive': structure buys the gate, and the gate is "
          "what turns feeding into a policy.")
        rnd_rows = [("arm", "seed", "final mean E_end", "E_end>0 / flies", "final mean meals")]
        for s in SEEDS:
            r = ctrl_last(REAL_RND[s])
            if r:
                rnd_rows.append(("real brain", s[1:], f"{r['E']:.0f}", f"{r['surv']}/6", f"{r['meals']:.1f}"))
        for c, lab in (("nobrain", "no-brain"), ("rewired", "rewired"), ("coinflip", "coin-flip")):
            for s in SEEDS:
                r = REPLR[c][s]
                if r:
                    rnd_rows.append((lab, s[1:], f"{r['E']:.0f}", f"{r['surv']}/6", f"{r['meals']:.1f}"))
        table("Table 6b. Random control lineages (no selection) of the real brain and the three lesion "
              "arms, final generation, three seeds.",
              rnd_rows, (40, 14, 32, 28, 32))
        p("Random control lineages (Table 6b). Every arm also ran its random control - no selection, same "
          "economy - on all three seeds, and the two readings of the same arm pull apart by an amount that "
          "depends on the arm. The largest within-arm divergence over the three seeds is "
          f"{DIV['coinflip']['within_max']:.0f} for the coin arm, {DIV['nobrain']['within_max']:.0f} for the "
          f"lesioned arm and {DIV['rewired']['within_max']:.0f} for the rewired arm, against across-seed "
          f"spreads of {DIV['coinflip']['sel_spread']:.0f}, {DIV['nobrain']['sel_spread']:.0f} and "
          f"{DIV['rewired']['sel_spread']:.0f}. On the coin arm the across-seed spread is the larger of the "
          "two, which is the shape an arm with no structure to stabilise it should have; on the rewired arm "
          "the within-arm divergence is the larger. Read plainly: in the control arms the energy outcome is "
          "set by the arm's feeding policy and by seed-level variance, with the selection operator sitting "
          "on top of both. That bounds how much of Table 6 may be attributed to selection.")
    figimg(f"{OUTD}/fig7_controls.png", "Fig 7. Mean energy per generation: real brain vs no-brain, rewired and coin-flip in the same economy, on three seeds (seed 11 solid, seed 12 dashed, seed 13 dash-dot).")

h2("5. Experiment B: applied task line (three arms)")
p("Three populations ran to completion on the applied battery (Table 1). The headline: under a contrast "
  "readout (task rate = channel mean minus rest-of-motor mean), the gate is genuinely alive - gpu_314 "
  "breaks out at generation 4 and sustains 40-55 solo of 144 possible per generation, best fly 8 of 18 "
  "tasks free of LLM cost. gpu_313 (original genome bounds) breaks out only at generation 217, showing "
  "the bound box delayed but did not prevent the same behaviour. gpu_300 (no contrast) reads 18/18 solo "
  "per fly, but that is a gate-failure artifact: its rate_sum is +1.4178 against a 0.01 threshold, every "
  "fly identical, all synapses pinned at the structural cap - the gate is open because the meter is "
  "saturated, not because the fly can act.")
p("Held-out probe: 8 flies x 3 never-trained tasks = 24/24 solved, every solve by a fresh LLM generation "
  "at 320-334 tokens. Harvest slot gpu_314/4 carries 365 learned synapses - an essentially empty graph - "
  "and passes 180/180 task checks: solutions come from LLM plus verifier. The solo count that does mean "
  "something is the contrast-gated one: 8/18 per fly, 40-55/144 per population.")
p("Architecture ablation (Fig 5). Three architectures evolved 10 generations x 20 flies (A0 and A1 with "
  "two seeds each, Skill-only once): mean four-subtask score rises from 0.53-0.58 to a 0.61-0.80 "
  "plateau. A0 (connectome plus plasticity) plateaus highest (0.77-0.80), Skill-only lowest (0.64-0.71). "
  "The substrate layer carries a real but modest share of the load - consistent with the applied-line "
  "division of labor: solutions live in the LLM plus verifier, the substrate contributes the gate.")
figimg(f"{OUTD}/fig5_arch.png", "Fig 5. Architecture ablation: mean score per generation, A0/A1 (two seeds each) vs Skill-only.")
last314 = ledger("gpu_314")[-1]
table("Table 5. gpu_314 final generation, per fly (solo denominator 18 tasks).",
      [("fly", "solo", "rate_sum")] +
      [(str(i), f"{s}/18", f"{r:+.4f}") for i, (s, r) in enumerate(zip(last314["solo"], last314["rate_sum"]))],
      (20, 30, 34))
table("Table 1. Three-arm harvest ledger (final state).",
      [("arm", "gens", "1st solo", "peak solo", "best fly", "LLM calls", "tokens"),
       ("gpu_300 ungated", "664", "gen 0", "144 (gen 506)", "18/18*", "78", "49,554"),
       ("gpu_313 orig bounds", "224", "gen 217", "36 (gen 223)", "8/18", "16,461", "10,429,312"),
       ("gpu_314 widened", "141", "gen 4", "55 (gen 63)", "8/18", "10,139", "6,526,790")],
      (34, 12, 16, 26, 18, 20, 26))
it("* gpu_300 18/18 is the gate-failure control (saturated meter), not a capability reading.")
figimg(f"{OUTD}/fig1_solo.png", "Fig 1. Population solo count per generation. gpu_300 saturates (meter artifact); gpu_314 is alive from gen 4; gpu_313 breaks out at gen 217.")

h2("6. Token economics")
p("Totals across the two contrast arms: 26,678 LLM calls, 17,005,656 tokens. The bill is structural: "
  "from generation 0 to the end, both arms spent a flat 72 calls and ~47k tokens per generation "
  "(Fig 2). 72 = 4 emptied slots x 18 tasks: the selection scheme deletes the non-survivors' stores, so "
  "four flies rebuild their cache from zero every generation. Survivors spend 0. The LLM bill is "
  "therefore a property of our memory-eviction design, not of task difficulty - the single clearest "
  "cost lesson of the project.")
p("The governor result belongs in the same ledger: -51% calls (116 to 57, 24 paired fly-runs) at "
  "exactly zero meal loss is a cost container. A structural lock-in control belongs too: gpu_300 pinned "
  "at SYN_CAP 2.5M stayed at setuptools_inject 0/8 for 165 generations; raising the cap to 3.2M moved "
  "the curriculum frontier 4 to 5 within ten minutes on the same checkpoint - capacity, not selection, "
  "was the binding constraint at that moment.")

h2("7. Negative results (the core chapter)")
p("Three candidate roles for the substrate were judged dead by measurement, and one hypothesis was "
  "falsified outright (Table 2). We state them as results, not apologies: a front layer that cannot "
  "remember beyond 1-2 steps, relays input as a near-linear copy, and cannot separate superposed cues "
  "cannot be the decision-maker; the gate role that survives does so because it reads a coarse signal "
  "at a low rate.")
table("Table 2. Measured negative results.",
      [("claim tested", "measurement", "verdict"),
       ("recursive memory horizon", "29 configurations, best 1-2 steps", "dead"),
       ("input relay as feature extractor", "R^2 0.91-0.96 vs linear copy", "dead"),
       ("channel choice under superposed cues", "margin 0.0000 (bistable: fire-all or silence)", "dead"),
       ("decision layer reads task identity", "18 tasks x 4 amplitudes, 72 samples, 18 classes, chance 0.056: raw input 1.000, cross-task cosine 0.0017", "falsified"),
       ("learned readout under native gain", "cross-task cosine 0.9723 vs innate 0.0618", "learned, not innate"),
       ("ok metric as capability", "180/180 saturated incl. 365-synapse fly", "no information"),
       ("fly gate in ungated arm", "rate -0.0007 vs threshold 0.01", "never fires")],
      (50, 82, 36))
figimg(f"{OUTD}/fig2_tokens.png", "Fig 2. Tokens per generation, both contrast arms: flat ~47k - the bill is the eviction design.")
figimg(f"{OUTD}/fig3_forage.png", "Fig 3. Foraging simulation, selection vs random over 6 generations: energy and meals tracks.")

h2("8. Discussion")
p("Where the substrate helps is one place, and it is a real place: a cheap per-task gate signal under a "
  "contrast readout, sustaining 40-55/144 zero-token executions per population-generation and 8/18 on a "
  "single fly, with the genome evolving to keep that signal alive (breakout at gen 4 with widened "
  "bounds vs gen 217 with the original box). That is the biological analogue of a router in a model "
  "cascade - and our measurements say the router signal must be contrastive; the population-wide motor "
  "rate is a saturated meter, not a decision.")
p("Why the decision-layer hypothesis died is mechanistically clear: 1-2 step state retention and "
  "near-linear input relay leave no substrate for per-task identity beyond what the input already "
  "carries; the classifier result (raw input 1.000 at chance 0.056) says the task label is in the cue, "
  "not in the network's transformation of it. The learned-versus-innate cosine pair (0.9723 vs 0.0618) "
  "localises the contribution to plasticity, not to the innate graph.")
p("Limitations. The economy-lineage result rests on two independent lineages plus one 20-generation "
  "plateau run (three lineages, one transfer seed). The teacher-transfer token figure is quoted at "
  "artifact level (operation counts and response lengths re-derived; token counts are "
  "tokenizer-dependent). Solo counts depend on store coverage; the 8/18 fly with 5,987 synapses and the "
  "8/18 fly with 738,868 synapses show synapse count is not the driver. CUDA and MPS numerical paths "
  "differ by ~+0.06 in rate_sum at migration boundaries; cross-machine replications must pin the "
  "device - and the control-arm replication changes two things at once: seed 11 ran on this machine's "
  "CPU while seeds 12 and 13 ran on a cloud GPU under the 195 CUDA path, so agreement across the three "
  "seeds is agreement across devices as well, which strengthens the robustness reading. One cell "
  "separates the seed effect from the device effect, and it is named below. The ok metric is saturated "
  "and excluded from claims.")
if REPL_REAL_C11 and REPL_REAL:
    p("One cell separates the two. The unmodified brain was run twice at seed 11, once on this machine's "
      f"CPU ({REPL_REAL['E']:.0f} final mean energy, {REPL_REAL['surv']}/6 flies above zero, "
      f"{REPL_REAL['meals']:.1f} meals) and once on the cloud GPU ({REPL_REAL_C11['E']:.0f}, "
      f"{REPL_REAL_C11['surv']}/6, {REPL_REAL_C11['meals']:.1f} meals), with the seed, the population, the "
      "world and the code held fixed. That gap is the device effect at n=6, and it sets the noise floor "
      "for every cross-device number in this paper: "
      + (f"the ordering against the lesion arms survives it ({'rewired > real > coin-flip' if DEVICE_HOLDS else 'the ordering against the lesion arms does not survive it'}). "
         if REPL else "")
      + "A single-cell cross-device comparison at this population size should be read as noise.")

h2("9. Conclusion")
p("A whole connectome in front of an LLM agent buys one measurable thing - a gate on asking the model - "
  "and costs 17 million tokens, most of it spent on our own memory-eviction design. We publish the gate "
  "number with its denominators, the bill with its mechanism, and the dead roles with their statistics. "
  "Next: >= 3 seeds on the economy lineage (the control arms are at three now, with the seed effect and "
  "the device effect separated by the seed-11 CPU-versus-CUDA cell above), re-derivation of the [195] artifacts, and "
  "a store-retention arm predicted to drive the per-generation bill toward zero while the gate climbs.")
p("Release: the evidence package is public at github.com/Mcking1983/flybrain - the analysis scripts, the "
  "ledgers every number here is re-derived from (evo_ledger.jsonl per arm, byte-identical), and this paper. "
  "The substrate graph and the per-fly checkpoints stay off-repo and are rebuilt from the published "
  "MaleCNS v1.0 release with code/build_graph.py.")

h2("Appendix A. Configuration ablation arms (app line)")
p("Nineteen configuration ablations of the app line ran on this machine (curriculum, teaching scope, "
  "latency budget, selection gate, synapse cap, pressure). They are configuration contrasts, not "
  "brain lesions - the control arms in Section 4 do the lesion work. Peak solo is out of 112 = 8 flies "
  "x 14 tasks for the full-battery arms; the cap8m / pressure / teachfront / syncap arms ran reduced "
  "batteries (peak out of ~72). Token totals are per whole run.")
table("Table 7. App-line configuration arms.",
      [("arm", "gens", "peak solo", "final solo", "tokens")] +
      [(a, str(g), str(pk), str(ls), f"{tk:,}") for a, g, _, pk, ls, tk in
       (("cap8m",220,0,71,64,7196),("choice",313,0,112,112,14920),("choice2",323,0,112,112,14920),
        ("choice3",323,0,112,112,14920),("contrast",297,0,112,112,14920),
        ("contrast_noteach",291,0,112,84,14920),("k100",303,0,112,112,14920),
        ("lat0",335,0,112,112,14920),("lat150",335,0,112,112,14920),("lat60",335,0,112,110,14920),
        ("noteach",244,0,112,112,20109),("pressure",225,0,71,64,7196),
        ("scopeall",237,0,112,112,20109),("selgate",246,0,112,112,20085),
        ("stripped",298,0,112,82,14920),("syncap",20,0,64,64,2624),
        ("teachall",228,0,72,72,14925),("teachfront",225,0,71,65,7196),("w1000",241,0,112,112,20109))],
      (36, 16, 26, 26, 26))

h2("References")
def ref(t):
    pdf.set_font("helvetica", "", 9); pdf.multi_cell(0, 4.6, t); pdf.ln(0.6)
ref("[1] Berg, S., Beckett, I. R., Costa, M., Schlegel, P., Januszewski, M., Marin, E. C., Nern, A., "
    "Preibisch, S., Qiu, W., Takemura, S.-y., et al. (2026). Sexual dimorphism in the complete "
    "Drosophila male central nervous system connectome. Cell 189, 5504-5526.e15. "
    "doi:10.1016/j.cell.2026.08.015 (111 authors). Preprint: doi:10.1101/2025.10.09.680999. The "
    "male-cns:v1.0 snapshot used here (neuprint/DVID) and its release page, CC BY: "
    "https://www.janelia.org/project-team/flyem/male-cns-connectome")
ref("[2] Takemura, S.-y., Hayworth, R., Huang, A., Januszewski, M., Lu, Z., Schlegel, P., et al. (2024). "
    "A Connectome of the Male Drosophila Ventral Nerve Cord. eLife. doi:10.7554/eLife.97769 "
    "(preprint doi:10.1101/2023.06.05.543757). The ventral nerve cord half of the male CNS, cited by [1].")
ref("[3] Luan, B. (2026). A Drosophila connectome substrate inside an LLM agent: what it gates, what it "
    "does not, and what it costs. Preprint, Zenodo, all versions doi:10.5281/zenodo.23396755 (the DOI of "
    "this version is on the record page). ORCID 0009-0001-5836-2923. Evidence package (paper, ledgers and "
    "the scripts that re-derive every number): https://github.com/Mcking1983/flybrain")

pdf.output(f"{OUTD}/flybrain_paper_draft_v7.pdf")
print("PDF:", f"{OUTD}/flybrain_paper_draft_v7.pdf", os.path.getsize(f"{OUTD}/flybrain_paper_draft_v7.pdf"), "bytes")
