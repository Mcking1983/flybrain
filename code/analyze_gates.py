"""Read gates_guide.json + gates_map.json (DATA only). For each closed cue X:
matrix [guided-toward gate x gate that actually responded when X is probed ALONE].
Diagonal = guidance reached its gate; off-diagonal = leakage into other gates.
Also: does X's opened-gate profile match the GUIDE's own innate profile ("route = guide's route")?
And how many neurons were born per gate route, and where they attached."""
import json, numpy as np
G=json.load(open("<DATA_ROOT>/gates_guide.json")); M=json.load(open("<DATA_ROOT>/gates_map.json"))
GN=M["gates"]; sizes=M["gate_sizes"]
def norm(v): v=np.array(v,float); return v/np.array([sizes[g] for g in GN])   # spikes per neuron in gate
for blk in G:
    X=blk["X"]; res=blk["results"]; alone=[r for r in res if "gate" not in r][0]; gr=[r for r in res if "gate" in r]
    print(f"\n================ X = {X}  (closed at birth to every gate) ================")
    print(f"{'guided toward':13s} {'guide':13s} | " + " ".join(f"{g[:8]:>8s}" for g in GN) + " |  born alive   syn  | own-gate  leak  match(guide)")
    print(f"{'(alone)':13s} {'-':13s} | " + " ".join(f"{v:8.0f}" for v in alone['end']) + f" | {alone['born']:5d} {alone['alive']:5d} {alone['syn']:5d} |")
    mat=[]; diag=[]; leak=[]; match=[]
    for r in gr:
        e=np.array(r["end"]); j=GN.index(r["gate"]); own=e[j]; other=e.sum()-own
        gp=np.array(r["guide_profile"]); 
        c=float(np.corrcoef(norm(e),norm(gp))[0,1]) if e.sum()>0 and gp.sum()>0 else float("nan")
        mat.append(norm(e)); diag.append(own>=5); leak.append(other/(e.sum()+1e-9)); match.append(c)
        print(f"{r['gate']:13s} {r['guide']:13s} | " + " ".join(f"{v:8.0f}" for v in e) + f" | {r['born']:5d} {r['alive']:5d} {r['syn']:5d} | {'OPEN' if own>=5 else 'shut':8s} {other/(e.sum()+1e-9):5.2f}  {c:+.2f}")
    print(f"  gates opened by their own guide: {sum(diag)}/{len(diag)} | mean leak fraction {np.nanmean(leak):.2f} | mean corr(X profile, guide innate profile) {np.nanmean(match):+.2f}")
    print(f"  neurons born: alone {alone['born']} vs guided {[r['born'] for r in gr]}")
    for r in gr: print(f"    -> {r['gate']:13s} new cells' inputs from {r['new_inputs_from']}")
    blk["_mat"]=np.array(mat); blk["_rows"]=[r["gate"] for r in gr]

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,len(G),figsize=(7.5*len(G),6))
ax=np.atleast_1d(ax)
for a,blk in zip(ax,G):
    m=blk["_mat"]; m=np.log1p(m*100)
    im=a.imshow(m,cmap="magma",aspect="auto"); a.set_xticks(range(len(GN))); a.set_xticklabels(GN,rotation=40,ha="right",fontsize=8)
    a.set_yticks(range(len(blk["_rows"]))); a.set_yticklabels([f"-> {g}" for g in blk["_rows"]],fontsize=8)
    a.set_xlabel("gate that responded (X probed ALONE)"); a.set_ylabel("guided toward"); a.set_title(f"X={blk['X']}: which doors open, log(spikes/neuron)")
    plt.colorbar(im,ax=a,fraction=0.04)
plt.tight_layout(); plt.savefig("<DATA_ROOT>/gates.png",dpi=110); print("\nsaved gates.png")
