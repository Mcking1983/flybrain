"""Read satiety.json + satiety_logs.json (DATA only). Does a stomach -- a brake in the BODY --
stop the reward-side runaway while keeping what was learned?"""
import json, numpy as np
R=json.load(open("<DATA_ROOT>/satiety.json")); L=json.load(open("<DATA_ROOT>/satiety_logs.json"))
arms=["satiety","always"]; nf=len(R["satiety"])
def learners(a): return [i for i,r in enumerate(R[a]) if r["food"]=="SNta31"]
print(f"flies per arm: {nf}  (SNta31-food flies = the ones that can learn: {learners('satiety')})\n")
print(f"{'arm':8s} {'eat late':>8s} {'probe food':>10s} {'probe neu':>9s} | {'reward%':>7s} {'hungry%':>7s} | {'syn end':>8s} {'syn max':>8s} {'last40':>7s} {'cold':>7s} {'bridges':>7s} | {'starved':>7s} {'E_end':>9s}")
for a in arms:
    Ls=[R[a][i] for i in learners(a)]; st=[r["first_starve"] for r in R[a]]
    print(f"{a:8s} {np.mean([r['eat_late'] for r in Ls]):8.2f} {np.mean([r['probe_food'] for r in Ls]):10.2f} {np.mean([r['probe_neu'] for r in R[a]]):9.2f} | "
          f"{np.mean([r['frac_plus'] for r in Ls]):7.2f} {np.mean([r['frac_hungry'] for r in Ls]):7.2f} | "
          f"{np.mean([r['syn'] for r in Ls]):8.0f} {np.mean([r['syn_max'] for r in Ls]):8.0f} {np.mean([r['syn_last40_growth'] for r in Ls]):+7.0f} {np.mean([r['cold'] for r in Ls]):7.0f} {np.mean([r['motor_syn'] for r in Ls]):7.0f} | "
          f"{sum(s is not None for s in st):4d}/{nf:<2d} {np.mean([r['E_end'] for r in Ls]):9.1f}")
print("\n--- paired, learners only (same seed): satiety vs always ---")
for i in learners("satiety"):
    s=R["satiety"][i]; w=R["always"][i]
    print(f"  fly {i}: syn {s['syn']:6d} vs {w['syn']:6d} ({s['syn']/max(w['syn'],1):.2f}x) | cold {s['cold']:5d} vs {w['cold']:6d} | probe food {s['probe_food']:.2f} vs {w['probe_food']:.2f} | starve@ {s['first_starve']} vs {w['first_starve']} | E_end {s['E_end']:8.1f} vs {w['E_end']:9.1f}")
print("\n--- did growth STOP? synapse count at ep 40/80/120/160, median learner ---")
for a in arms:
    S=np.array([[l["syn"] for l in L[a][i]] for i in learners(a)]); m=np.median(S,0)
    print(f"  {a:8s} " + "  ".join(f"ep{e:3d}:{m[min(e,len(m))-1]:7.0f}" for e in (40,80,120,160)) + f"  | growth per ep, last quarter: {(m[-1]-m[-40])/40:+.1f}")
print("\n--- the rhythm (satiety, median learner): hungry / reward per 20-episode block ---")
i=learners("satiety")[0]; lg=L["satiety"][i]
for b in range(0,len(lg),20):
    blk=lg[b:b+20]; print(f"  ep {b:3d}-{b+19:3d}: hungry {np.mean([l['hungry'] for l in blk]):.2f}  reward(M=+1) {np.mean([l['M']>0 for l in blk]):.2f}  ate {sum(l['ate'] for l in blk):2d}  stomach mean {np.mean([l['S'] for l in blk]):.1f}  syn {blk[-1]['syn']:6d}")

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,ax=plt.subplots(2,2,figsize=(14,9)); cols={"satiety":"#2a9d8f","always":"#e9c46a"}
for a in arms:
    li=learners(a); S=np.array([[l["syn"] for l in L[a][i]] for i in li]); C=np.array([[l["cold"] for l in L[a][i]] for i in li]); E=np.array([[l["E"] for l in L[a][i]] for i in li])
    ax[0,0].plot(np.median(S,0),color=cols[a],label=f"{a} (hot+cold)"); ax[0,0].plot(np.median(C,0),"--",color=cols[a],label=f"{a} cold")
    ax[0,1].plot(np.median(E,0),color=cols[a],label=a)
    ws=[c["w"] for c in R[a][0]["curve"]]; ax[1,0].plot(ws,np.mean([[c["eat_food_alone"] for c in R[a][i]["curve"]] for i in li],0),"o-",color=cols[a],label=a)
    M=np.array([[float(l["M"]>0) for l in L[a][i]] for i in li]).mean(0); k=10; ax[1,1].plot(np.convolve(M,np.ones(k)/k,mode="valid"),color=cols[a],label=f"{a} reward rate")
H=np.array([[l["hungry"] for l in L["satiety"][i]] for i in learners("satiety")]).mean(0); ax[1,1].plot(np.convolve(H,np.ones(10)/10,mode="valid"),":",color="#e76f51",label="satiety: hungry rate")
ax[0,0].set_title("GROWN SYNAPSES, learners (median): does the stomach stop the runaway?"); ax[0,0].set_yscale("symlog"); ax[0,0].set_xlabel("episode")
ax[0,1].set_title("ENERGY, learners (median; 0 = starved)"); ax[0,1].axhline(0,color="k",lw=0.8,ls="--"); ax[0,1].set_xlabel("episode")
ax[1,0].set_title("LEARNING kept? eat rate on food-ALONE"); ax[1,0].set_ylim(-0.05,1.05); ax[1,0].set_xlabel("round")
ax[1,1].set_title("THE RHYTHM: reward fires only when hungry (10-ep moving avg)"); ax[1,1].set_ylim(-0.05,1.05); ax[1,1].set_xlabel("episode")
for a_ in ax.ravel(): a_.legend(fontsize=8)
plt.tight_layout(); plt.savefig("<DATA_ROOT>/satiety.png",dpi=110); print("\nsaved satiety.png")
