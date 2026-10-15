#!/usr/bin/env python3
"""Real-brain lineage (no lesion) on THIS device. Same driver path as ctrl_run.py,
minus any brain patch. Writes <OUTD>/ctrl_real_evolve_desire_{select,random}.json

Run it the way the two real-brain cells of paper v6 were produced (one per seed):
  FLY_GRAPH=<path to malecns_graph.npz> SEED=12 OUTD=<dir> python3 real_run.py
  FLY_GRAPH=<path to malecns_graph.npz> SEED=11 OUTD=<dir> python3 real_run.py
SEED / POP / GENS / ROUNDS / FOOD / CSYN are read by fly_evolve_desire.py from the
environment; the defaults reproduce the published world (POP=6, GENS=6, ROUNDS=30,
FOOD=12, CSYN=3e-4).
"""
import os, types
OUTD = os.path.expanduser(os.environ.get("OUTD", "~/flybrain/ctrl"))
os.makedirs(OUTD, exist_ok=True)
SRC = os.path.expanduser(os.environ.get("FLY_SRC", "~/flybrain/fly_evolve_desire.py"))
# the output prefix hard-coded inside fly_evolve_desire.py, rewritten here to OUTD
SRC_OUT = os.environ.get("FLY_SRC_OUT", "/srv/fast/flybrain/evolve_desire")
src = open(SRC).read()
code = src.replace(SRC_OUT, f"{OUTD}/ctrl_real_evolve_desire")
mod = types.ModuleType("fe_real")
mod.__dict__["__name__"] = "fe_real"
exec(compile(code, "fe_real", "exec"), mod.__dict__)
print(f"REAL SEED={mod.SEED} POP={mod.POP} GENS={mod.GENS} ROUNDS={mod.ROUNDS} "
      f"FOOD={mod.fd.FOOD} CSYN={mod.fd.C_SYN} OUTD={OUTD}", flush=True)
mod.lineage("select", True, mod.SEED)
mod.lineage("random", False, mod.SEED)
print("DONE real", flush=True)
