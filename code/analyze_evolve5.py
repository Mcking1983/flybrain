"""Read evolve5_s{11,23}_{select,random}.json (DATA only; works on partial runs). Three criteria set by the user:
(1) does the SELECTED lineage's probe-set score rise across generations (vs random-parent control)?
(2) do genes move DIRECTIONALLY: |drift_select| >= 2x |drift_random| AND same sign in both seeds?
(3) does the round-2 seek rate rise?  Plus: runaway watch (synapses / cold per generation)."""
import json, os, numpy as np, warnings; warnings.filterwarnings("ignore")
SEEDS=[11,23]; L=["select","random"]; keys=["p_sprout","birth_per","cold_streak","eta","hot_decay","p_inh","k_syn","r_high"]
H={}
for s in SEEDS:
    for l in L:
        f=f"<DATA_ROOT>/evolve5_s{s}_{l}.json"
        if os.path.exists(f): H[(s,l)]=json.load(open(f))
if not H: print("no data yet"); raise SystemExit
G=min(len(h) for h in H.values()); print(f"generations available (min across runs): {G}   runs: {sorted(H)}\n")
def gm(s,l,g,k,f=np.mean):
    v=[r[k] for r in H[(s,l)][g]["results"] if r.get(k) is not None]; return f(v) if v else float("nan")
for s in SEEDS:
    for l in L:
        if (s,l) not in H: continue
        print(f"===== seed {s} {l.upper()} =====")
        print(f"{'gen':>3s} | {'score':>5s} {'max':>4s} | {'seek':>4s} {'A+H':>4s} {'none':>4s} | {'rd2 seek':>8s} | {'surv':>4s} {'E':>5s} | {'syn':>6s} {'cold':>6s} | " + " ".join(f"{k:>9s}" for k in keys))
        for g in range(len(H[(s,l)])):
            res=H[(s,l)][g]["results"]; es=[r["early_seek"] for r in res if r["early_seek"] is not None]
            print(f"{g:3d} | {gm(s,l,g,'score'):5.3f} {gm(s,l,g,'score',np.max):4.2f} | {gm(s,l,g,'seek_ok'):4.2f} {gm(s,l,g,'ah_ok'):4.2f} {gm(s,l,g,'none_ok'):4.2f} | {np.mean(es) if es else float('nan'):8.2f} | {len(H[(s,l)][g]['survivors']):4d} {gm(s,l,g,'E_end'):5.0f} | {gm(s,l,g,'syn'):6.0f} {gm(s,l,g,'cold'):6.0f} | " + " ".join(f"{np.mean([r['genome'][k] for r in res]):9.3g}" for k in keys))
        print()
print("===== CRITERION 1: score trend, select vs random (gen0 -> last common gen, and slope) =====")
for s in SEEDS:
    if (s,"select") in H and (s,"random") in H:
        n=min(len(H[(s,"select")]),len(H[(s,"random")]))
        for l in L:
            sc=[gm(s,l,g,"score") for g in range(n)]; slope=np.polyfit(range(n),sc,1)[0] if n>1 else float("nan")
            print(f"  seed {s} {l:6s}: score {sc[0]:.3f} -> {sc[-1]:.3f}  (slope {slope:+.4f}/gen over {n} gens)")
print("\n===== CRITERION 2: directional genes  (|Δlog select| >= 2x |Δlog random| in BOTH seeds, same sign) =====")
verdict={}
for k in keys:
    rows=[]
    for s in SEEDS:
        if (s,"select") in H and (s,"random") in H:
            n=min(len(H[(s,"select")]),len(H[(s,"random")]))
            if n<2: continue
            d={}
            for l in L:
                v0=np.mean([r["genome"][k] for r in H[(s,l)][0]["results"]]); v1=np.mean([r["genome"][k] for r in H[(s,l)][n-1]["results"]]); d[l]=np.log(v1/v0)
            rows.append((s,d["select"],d["random"]))
    if len(rows)==2:
        ok=all(abs(ds)>=2*abs(dr) and abs(ds)>0.1 for _,ds,dr in rows) and np.sign(rows[0][1])==np.sign(rows[1][1])
        verdict[k]=ok
        print(f"  {k:11s} " + " | ".join(f"seed {s}: select {ds:+.2f} random {dr:+.2f}" for s,ds,dr in rows) + ("   <== DIRECTIONAL GENE" if ok else ""))
    elif rows: print(f"  {k:11s} only one seed so far: select {rows[0][1]:+.2f} random {rows[0][2]:+.2f}")
print("\n===== CRITERION 3: round-2 seek rate (Baldwin-ward) =====")
for s in SEEDS:
    for l in L:
        if (s,l) in H:
            es=[]
            for g in range(len(H[(s,l)])):
                e=[r["early_seek"] for r in H[(s,l)][g]["results"] if r["early_seek"] is not None]; es.append(np.mean(e) if e else float("nan"))
            print(f"  seed {s} {l:6s}: " + " ".join(f"{x:.2f}" for x in es))
print("\n===== GROWTH TABLE (user): per gen population mean syn / cold, and top-4 parents' mean syn / cold =====")
for s in SEEDS:
    for l in L:
        if (s,l) not in H: continue
        print(f"  seed {s} {l:6s}:")
        prev=None
        for g in range(len(H[(s,l)])):
            R=H[(s,l)][g]["results"]; top=[R[i] for i in H[(s,l)][g]["order"][:4]]
            sc=np.mean([r["score"] for r in R]); sy=np.mean([r["syn"] for r in R]); co=np.mean([r["cold"] for r in R])
            flag=" ** GROWTH WITHOUT SCORE GAIN **" if (l=="select" and prev and (sc-prev[0])<=0.05 and sy>prev[1]) else ""
            print(f"    g{g}: score {sc:.3f}  syn {sy:6.0f}  cold {co:6.0f}  | top4 syn {np.mean([r['syn'] for r in top]):6.0f} cold {np.mean([r['cold'] for r in top]):6.0f}{flag}")
            prev=(sc,sy)
print("\n===== RUNAWAY WATCH: mean synapses / cold per gen =====")
for s in SEEDS:
    for l in L:
        if (s,l) in H: print(f"  seed {s} {l:6s}: syn " + " ".join(f"{gm(s,l,g,'syn'):.0f}" for g in range(len(H[(s,l)]))) + "  | cold " + " ".join(f"{gm(s,l,g,'cold'):.0f}" for g in range(len(H[(s,l)]))))
