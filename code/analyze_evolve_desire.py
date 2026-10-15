"""Read evolve_desire_{select,random}.json (DATA only). Is there a gene? Compare the selected lineage
with the random-parent control: does it get better, learn earlier, and do genome parameters drift?"""
import json, os, numpy as np, warnings; warnings.filterwarnings("ignore")
TAG=os.environ.get("TAG",""); SUF=("_"+TAG) if TAG else ""
H={l:json.load(open(f"<DATA_ROOT>/evolve_desire{SUF}_{l}.json")) for l in ("select","random")}
G=len(H["select"]); keys=["p_sprout","birth_per","cold_streak","eta","hot_decay","p_inh","k_syn","r_high"]
def gm(l,g,k,f=np.mean): v=[r[k] for r in H[l][g]["results"] if r[k] is not None]; return f(v) if v else float("nan")
print(f"{G} generations, {len(H['select'][0]['results'])} per generation\n")
for l in ("select","random"):
    print(f"===== {l.upper()} lineage =====")
    print(f"{'gen':>3s} | {'E_end':>7s} {'best E':>7s} {'meals':>5s} | {'D_gate':>6s} {'D_seek':>6s} | {'early gate':>8s} {'early seek':>8s} | {'t_gate':>6s} {'n':>3s} {'t_seek':>6s} {'n':>3s} | {'leak':>4s} {'seek':>4s} | {'syn':>5s} {'cold':>4s}")
    for g in range(G):
        res=H[l][g]["results"]; tg=[r["t_gate"] for r in res if r["t_gate"] is not None]; ts=[r["t_seek"] for r in res if r["t_seek"] is not None]
        print(f"{g:3d} | {gm(l,g,'E_end'):7.1f} {gm(l,g,'E_end',np.max):7.1f} {gm(l,g,'meals'):5.1f} | {gm(l,g,'D_gate'):+6.2f} {gm(l,g,'D_seek'):+6.2f} | {gm(l,g,'early_gate'):+8.2f} {gm(l,g,'early_seek'):+8.2f} | {np.mean(tg) if tg else float('nan'):6.1f} {len(tg):3d} {np.mean(ts) if ts else float('nan'):6.1f} {len(ts):3d} | {gm(l,g,'act_A_full'):4.2f} {gm(l,g,'act_none_hungry'):4.2f} | {gm(l,g,'syn'):5.0f} {gm(l,g,'cold'):4.0f}")
    print()
print("===== GENOME drift (population mean per generation; log-scale params shown as-is) =====")
for l in ("select","random"):
    print(f"--- {l} ---"); print(f"{'gen':>3s} " + " ".join(f"{k:>10s}" for k in keys))
    for g in range(G):
        print(f"{g:3d} " + " ".join(f"{np.mean([r['genome'][k] for r in H[l][g]['results']]):10.3g}" for k in keys))
print("\n===== the verdict =====")
d0=lambda l,k: gm(l,0,k); dN=lambda l,k: gm(l,G-1,k)
for k,lab in [("E_end","energy at end of life"),("meals","meals"),("D_gate","gating (hungry-only eating)"),("D_seek","seeking"),("early_gate","gating at FIRST probe (innate-ward)"),("early_seek","seeking at FIRST probe (innate-ward)")]:
    print(f"  {lab:42s} select gen0 {d0('select',k):+7.2f} -> gen{G-1} {dN('select',k):+7.2f}   |   random gen0 {d0('random',k):+7.2f} -> gen{G-1} {dN('random',k):+7.2f}")
print("  genome params that moved in the SELECTED lineage but not the random one (|Δ select| > 2×|Δ random|, on log scale for log params):")
for k in keys:
    s0=np.mean([r['genome'][k] for r in H['select'][0]['results']]); sN=np.mean([r['genome'][k] for r in H['select'][G-1]['results']])
    r0=np.mean([r['genome'][k] for r in H['random'][0]['results']]); rN=np.mean([r['genome'][k] for r in H['random'][G-1]['results']])
    ds=np.log(sN/s0); dr=np.log(rN/r0)
    flag="  <-- candidate gene" if abs(ds)>2*abs(dr) and abs(ds)>0.2 else ""
    print(f"    {k:11s} select {s0:8.3g} -> {sN:8.3g} (Δlog {ds:+.2f})   random {r0:8.3g} -> {rN:8.3g} (Δlog {dr:+.2f}){flag}")

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
c={"select":"#2a9d8f","random":"#e9c46a"}; gens=list(range(G))
fig,ax=plt.subplots(2,3,figsize=(18,9))
for l in ("select","random"):
    ax[0,0].plot(gens,[gm(l,g,"E_end") for g in gens],"o-",color=c[l],label=f"{l} mean"); ax[0,0].plot(gens,[gm(l,g,"E_end",np.max) for g in gens],"s--",color=c[l],label=f"{l} best")
    ax[0,1].plot(gens,[gm(l,g,"D_gate") for g in gens],"o-",color=c[l],label=f"{l} gate"); ax[0,1].plot(gens,[gm(l,g,"D_seek") for g in gens],"s--",color=c[l],label=f"{l} seek")
    ax[0,2].plot(gens,[gm(l,g,"early_gate") for g in gens],"o-",color=c[l],label=f"{l} gate @first probe"); ax[0,2].plot(gens,[gm(l,g,"early_seek") for g in gens],"s--",color=c[l],label=f"{l} seek @first probe")
    tg=[np.mean([r["t_gate"] for r in H[l][g]["results"] if r["t_gate"] is not None] or [np.nan]) for g in gens]; ts=[np.mean([r["t_seek"] for r in H[l][g]["results"] if r["t_seek"] is not None] or [np.nan]) for g in gens]
    ax[1,0].plot(gens,tg,"o-",color=c[l],label=f"{l} time-to-gate"); ax[1,0].plot(gens,ts,"s--",color=c[l],label=f"{l} time-to-seek")
    ax[1,1].plot(gens,[gm(l,g,"meals") for g in gens],"o-",color=c[l],label=f"{l} meals"); ax[1,1].plot(gens,[gm(l,g,"act_A_full") for g in gens],"s--",color=c[l],label=f"{l} full-leak")
for i,k in enumerate(keys):
    for l,ls in (("select","-"),("random","--")):
        v=np.array([np.mean([r['genome'][k] for r in H[l][g]['results']]) for g in gens]); ax[1,2].plot(gens,np.log(v/v[0]),ls,color=plt.cm.tab10(i),label=f"{k} ({l})" if l=="select" else None)
ax[0,0].set_title("the world's verdict: energy at end of life"); ax[0,1].set_title("behaviour: gate & seek at end of life"); ax[0,2].set_title("innate-ward? behaviour at first probe (Baldwin)")
ax[1,0].set_title("time to learn (round of first appearance)"); ax[1,1].set_title("meals & full-leak"); ax[1,2].set_title("genome drift, log(param/gen0): solid=select, dashed=random"); ax[1,2].axhline(0,color="k",lw=0.8)
for a in ax.ravel(): a.set_xlabel("generation"); a.legend(fontsize=7)
plt.tight_layout(); plt.savefig(f"<DATA_ROOT>/evolve_desire{SUF}.png",dpi=110); print(f"\nsaved evolve_desire{SUF}.png")
