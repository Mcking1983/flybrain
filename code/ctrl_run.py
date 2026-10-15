#!/usr/bin/env python3
"""Control arms for the foraging economy (paper v3): no-brain / rewired / coin-flip.

Same world as the select-vs-random lineages (upkeep 3e-4, meal 12, POP=6, GENS=6, ROUNDS=30,
SEED=11/12). Only the brain changes:
  nobrain  - innate connectome W zeroed (structure gone, plasticity still grows learned synapses)
  rewired  - W's weights permuted across the same edges (degree preserved, structure destroyed)
  coinflip - action decision replaced by a coin (eng>=0.5 -> rng.random()<0.5); learning continues
Writes $OUTD/ctrl_<CTRL>_evolve_desire_<label>.json (default ~/flybrain/ctrl), same schema as
fly_evolve_desire. SEED/POP/GENS/ROUNDS come from the environment, as in the world driver.
"""
import json, os, sys, numpy as np
import scipy.sparse as sp

OUTD = os.path.expanduser(os.environ.get("OUTD", "~/flybrain/ctrl"))
os.makedirs(OUTD, exist_ok=True)
sys.path.insert(0, os.path.expanduser("~/flybrain"))
import fly_select as fs, fly_desire as fd

CTRL = os.environ.get("CTRL", "nobrain")

# ---- patch the brain ----
if CTRL == "nobrain":
    fd.W = sp.csr_matrix((np.zeros_like(fd.W.data), fd.W.indices, fd.W.indptr), shape=fd.W.shape)
elif CTRL == "rewired":
    rngp = np.random.default_rng(777)
    fd.W = sp.csr_matrix((rngp.permutation(fd.W.data), fd.W.indices, fd.W.indptr), shape=fd.W.shape)
elif CTRL == "coinflip":
    pass  # handled in live below
else:
    raise SystemExit(f"unknown CTRL={CTRL}")

if CTRL == "coinflip":
    # copy of fd.live with the action rule replaced by a coin; everything else identical
    import torch
    from fly_desire import (stim, tid, GrowFly, inborn_tensor, eng_of, census, E0, C_SPIKE,
                            C_SYN, C_NEU, M_REF, DIGEST, S_FULL, P_FORAGE, A_NAME, COMP, H_NAME,
                            KINDS, N)
    def coin_live(arm, seed):
        rng = np.random.default_rng(seed)
        fly = GrowFly(inborn_tensor(fd.W), rng)
        A, c = tid[A_NAME], tid[COMP]
        H = tid[H_NAME]; useH = True
        E = E0; S = 0.0; log = []; traj = []
        for rd in range(fd.ROUNDS):
            for kind in rng.permutation(KINDS):
                hungry = S < S_FULL; paired = kind.endswith("+c"); see_food = kind.startswith("A")
                cues = ([A] if see_food else []) + ([c] if paired else []) + ([H] if (useH and hungry) else [])
                acc = fly.run(stim(*cues)) if cues else fly.run(torch.zeros(N))
                eng = eng_of(acc); acted = rng.random() < 0.5          # THE COIN
                got = acted and (see_food or rng.random() < P_FORAGE)
                income = fd.FOOD * eng if got else 0.0
                cost = C_SPIKE * float(acc.sum()) + C_SYN * len(fly.gm) + C_NEU * int(fly.alive.sum())
                E += income - cost
                if got: S += income
                S *= DIGEST
                M = 1.0 if (got and hungry) else (-1.0 if (acted and not hungry) else 0.0)
                fly.step(acc, M)
                log.append(dict(rd=rd, kind=kind, hungry=int(hungry), acted=int(acted), got=int(got),
                                M=M, E=round(E, 1), syn=int(len(fly.gm)), alive=int(fly.alive.sum())))
            if (rd + 1) % fd.PROBE == 0:
                cs = census(fly, A, H); cs["rd"] = rd + 1; traj.append(cs)
        end = traj[-1]
        last = [l for l in log if l["rd"] >= fd.ROUNDS - 10]
        def rate(sel):
            v = [l["acted"] for l in last if sel(l)]; return float(np.mean(v)) if v else float("nan")
        beh = dict(act_A_hungry=rate(lambda l: l["kind"] == "A" and l["hungry"]),
                   act_A_full=rate(lambda l: l["kind"] == "A" and not l["hungry"]),
                   act_none_hungry=rate(lambda l: l["kind"] == "none" and l["hungry"]),
                   act_none_full=rate(lambda l: l["kind"] == "none" and not l["hungry"]),
                   frac_hungry=float(np.mean([l["hungry"] for l in log])),
                   meals=int(sum(l["got"] for l in log)),
                   wasted=int(sum(1 for l in log if l["acted"] and not l["hungry"])))
        return dict(arm=arm, D_gate=end["engAH"] - end["engA"], D_seek=end["engH"] - end["eng0"],
                    **{k: end[k] for k in ("engA", "engAH", "engH", "eng0", "gated_new", "gated_inborn",
                                           "drive_new", "drive_inborn", "gated_inborn_sc")},
                    **beh, E_end=round(E, 1), syn=int(len(fly.gm)), cold=int(fly.gk.sum()),
                    alive=int(fly.alive.sum()), born=fly.born, traj=traj, log=log)
    fd.live = coin_live

# ---- reuse fly_evolve_desire machinery with redirected output ----
import fly_evolve_desire as fe
fe.fd.live = fd.live  # ensure the patched live is used
_orig_dump = json.dump

import types
src = open(os.path.expanduser("~/flybrain/fly_evolve_desire.py")).read()
# monkey the dump path inside lineage by wrapping json.dump for that filename pattern
def dump_wrap(obj, fh, *a, **k):
    return _orig_dump(obj, fh, *a, **k)
fe.json.dump = dump_wrap
# simplest: override the path by chdir trick is fragile; patch fe.lineage's open via string exec
code = src.replace('/srv/fast/flybrain/evolve_desire', f'{OUTD}/ctrl_{CTRL}_evolve_desire')
mod = types.ModuleType("fe_ctrl")
mod.__dict__["__name__"] = "fe_ctrl"
exec(compile(code, "fe_ctrl", "exec"), mod.__dict__)
mod.fd.live = fd.live
print(f"CTRL={CTRL} SEED={mod.SEED} POP={mod.POP} GENS={mod.GENS} ROUNDS={mod.ROUNDS} "
      f"FOOD={mod.fd.FOOD} CSYN={mod.fd.C_SYN}", flush=True)
mod.lineage("select", True, mod.SEED)
mod.lineage("random", False, mod.SEED)
print("DONE", CTRL, flush=True)
