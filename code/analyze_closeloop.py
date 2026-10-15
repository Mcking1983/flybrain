"""Read closeloop.json + closeloop_logs.json (DATA only). Did the fly learn to reach food it
could not reach at birth, driven only by its world? And what did closing the loop cost it?"""
import json, numpy as np
R=json.load(open("<DATA_ROOT>/closeloop.json")); L=json.load(open("<DATA_ROOT>/closeloop_logs.json"))
arms=[a for a in ["closedloop","noconseq","nopair","shuffled"] if R.get(a)]
nf=len(R[arms[0]]); print(f"flies per arm: {nf}\n")
def col(a,k): return np.array([r[k] for r in R[a]],dtype=float)
print(f"{'arm':10s} {'eat early':>9s} {'eat late':>8s} {'learned':>8s} {'neu act late':>12s} {'probe food':>10s} {'probe neu':>9s} | {'motor_syn':>9s} {'cold':>7s} {'starved':>8s} {'starve@':>7s}")
for a in arms:
    e0=col(a,"eat_early"); e1=col(a,"eat_late"); n1=col(a,"actneu_late"); pf=col(a,"probe_food"); pn=col(a,"probe_neu")
    learned=int(((e1>=0.5)&(e0<0.5)).sum()); st=[r["first_starve"] for r in R[a]]; sv=[s for s in st if s is not None]
    print(f"{a:10s} {e0.mean():9.2f} {e1.mean():8.2f} {learned:5d}/{nf:<2d} {n1.mean():12.2f} {pf.mean():10.2f} {pn.mean():9.2f} | {col(a,'motor_syn').mean():9.0f} {col(a,'cold').mean():7.0f} {len(sv):5d}/{nf:<2d} {np.mean(sv) if sv else float('nan'):7.1f}")

print("\n--- per fly: closedloop learned? (food cue, eat late, probe food, probe neu, syn, starve@) ---")
for i,r in enumerate(R["closedloop"]):
    print(f"  fly {i} food={r['food']:8s} eat {r['eat_early']:.2f}->{r['eat_late']:.2f} probe food {r['probe_food']:.2f} neu {r['probe_neu']:.2f} | ate alone {r['ate_alone']:3d} | syn {r['syn']:7d} cold {r['cold']:6d} | starve@{r['first_starve']}")

print("\n--- how often did the world speak, closedloop (fraction of episodes with M=+1 / M=-1 / M=0) ---")
for i,log in enumerate(L["closedloop"]):
    Ms=np.array([l["M"] for l in log]); print(f"  fly {i}: +1 {np.mean(Ms>0):.2f}  -1 {np.mean(Ms<0):.2f}  0 {np.mean(Ms==0):.2f}")

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,ax=plt.subplots(2,2,figsize=(14,9)); cols={"closedloop":"#2a9d8f","noconseq":"#e9c46a","nopair":"#e76f51","shuffled":"#8ab17d"}
for a in arms:
    ws=[c["w"] for c in R[a][0]["curve"]]
    ax[0,0].plot(ws,np.mean([[c["eat_food_alone"] for c in r["curve"]] for r in R[a]],0),"o-",color=cols[a],label=a)
    ax[0,1].plot(ws,np.mean([[c["act_neu_alone"] for c in r["curve"]] for r in R[a]],0),"o-",color=cols[a],label=a)
    E=np.array([[l["E"] for l in log] for log in L[a]]); S=np.array([[l["syn"] for l in log] for log in L[a]])
    ax[1,0].plot(np.median(E,0),color=cols[a],label=a); ax[1,1].plot(np.median(S,0),color=cols[a],label=a)
ax[0,0].set_title("LEARNING: eat rate when food appears ALONE (could not at birth)"); ax[0,0].set_xlabel("round"); ax[0,0].set_ylim(-0.05,1.05)
ax[0,1].set_title("DISCIPLINE: act rate when neutral appears ALONE (should stay low)"); ax[0,1].set_xlabel("round"); ax[0,1].set_ylim(-0.05,1.05)
ax[1,0].set_title("ENERGY (median fly; world accounting, 0 = starved)"); ax[1,0].axhline(0,color="k",lw=0.8,ls="--"); ax[1,0].set_xlabel("episode")
ax[1,1].set_title("GROWN SYNAPSES (median fly): does consolidation run away?"); ax[1,1].set_xlabel("episode"); ax[1,1].set_yscale("symlog")
for a_ in ax.ravel(): a_.legend(fontsize=8)
plt.tight_layout(); plt.savefig("<DATA_ROOT>/closeloop.png",dpi=110); print("\nsaved closeloop.png")
