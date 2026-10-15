"""Read economy.json (DATA only). Where is break-even for a learning brain, and does a cheap world
stop telling a stable brain from a runaway?"""
import json, numpy as np
O=json.load(open("<DATA_ROOT>/economy.json"))
CS=sorted({o["C_SYN"] for o in O},reverse=True); FD=sorted({o["FOOD"] for o in O}); arms=["satiety","always"]
def cell(c,f,a): return [o for o in O if o["C_SYN"]==c and o["FOOD"]==f and o["arm"]==a][0]["flies"]
nf=len(cell(CS[0],FD[0],"satiety"))
print(f"{nf} flies per cell, {len(cell(CS[0],FD[0],'satiety')[0]['E_traj'])*4} episodes\n")
for a in arms:
    print(f"===== {a.upper()} =====")
    print(f"{'C_SYN':>7s} {'FOOD':>5s} | {'survived':>8s} {'starve@':>14s} | {'E_end':>9s} {'E_min':>9s} | {'learned':>7s} {'probe':>5s} | {'syn':>7s} {'last40':>7s} {'cold':>7s} | {'reward%':>7s}")
    for c in CS:
        for f in FD:
            fl=cell(c,f,a); st=[x["first_starve"] for x in fl]
            print(f"{c:7.0e} {f:5.0f} | {sum(x['survived'] for x in fl):5d}/{nf:<2d} {str([s for s in st]):>14s} | {np.mean([x['E_end'] for x in fl]):9.1f} {np.mean([x['E_min'] for x in fl]):9.1f} | {np.mean([x['eat_late'] for x in fl]):7.2f} {np.mean([x['probe_food'] for x in fl]):5.2f} | {np.mean([x['syn'] for x in fl]):7.0f} {np.mean([x['last40'] for x in fl]):+7.0f} {np.mean([x['cold'] for x in fl]):7.0f} | {np.mean([x['reward_frac'] for x in fl]):7.2f}")
    print()
print("===== does the world still tell stable from runaway?  (survived: satiety | always ; E_end: satiety | always) =====")
for c in CS:
    for f in FD:
        s=cell(c,f,"satiety"); w=cell(c,f,"always")
        ss=sum(x['survived'] for x in s); sw=sum(x['survived'] for x in w)
        verdict = "both die" if ss==0 and sw==0 else ("SELECTS: stable lives, runaway dies" if ss>sw else ("both live: world blind to runaway" if ss==nf and sw==nf else "mixed"))
        print(f"  C_SYN {c:.0e} FOOD {f:3.0f}: {ss}/{nf} | {sw}/{nf}   E_end {np.mean([x['E_end'] for x in s]):9.1f} | {np.mean([x['E_end'] for x in w]):9.1f}   syn {np.mean([x['syn'] for x in s]):7.0f} | {np.mean([x['syn'] for x in w]):7.0f}   -> {verdict}")

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,ax=plt.subplots(2,3,figsize=(17,9))
for j,a in enumerate(arms):
    M=np.array([[sum(x['survived'] for x in cell(c,f,a))/nf for f in FD] for c in CS])
    im=ax[0,j].imshow(M,cmap="RdYlGn",vmin=0,vmax=1,aspect="auto"); ax[0,j].set_xticks(range(len(FD))); ax[0,j].set_xticklabels([f"FOOD={f:.0f}" for f in FD]); ax[0,j].set_yticks(range(len(CS))); ax[0,j].set_yticklabels([f"upkeep {c:.0e}" for c in CS])
    for i in range(len(CS)):
        for k in range(len(FD)): ax[0,j].text(k,i,f"{M[i,k]:.2f}",ha="center",va="center",fontsize=11)
    ax[0,j].set_title(f"{a}: fraction surviving 160 episodes")
# learning speed vs richness (satiety)
L=np.array([[np.mean([x['eat_late'] for x in cell(c,f,'satiety')]) for f in FD] for c in CS])
im=ax[0,2].imshow(L,cmap="viridis",vmin=0,vmax=1,aspect="auto"); ax[0,2].set_xticks(range(len(FD))); ax[0,2].set_xticklabels([f"FOOD={f:.0f}" for f in FD]); ax[0,2].set_yticks(range(len(CS))); ax[0,2].set_yticklabels([f"upkeep {c:.0e}" for c in CS])
for i in range(len(CS)):
    for k in range(len(FD)): ax[0,2].text(k,i,f"{L[i,k]:.2f}",ha="center",va="center",fontsize=11,color="w")
ax[0,2].set_title("satiety: learned? (eat rate on food-ALONE, late)")
# energy trajectories per world, median fly, both arms
cols=plt.cm.tab10(np.linspace(0,1,len(CS)*len(FD)))
for j,a in enumerate(arms):
    k=0
    for c in CS:
        for f in FD:
            E=np.median(np.array([x["E_traj"] for x in cell(c,f,a)]),0); ax[1,j].plot(np.arange(len(E))*4,E,color=cols[k],label=f"upkeep {c:.0e} food {f:.0f}"); k+=1
    ax[1,j].axhline(0,color="k",lw=0.8,ls="--"); ax[1,j].set_title(f"{a}: energy (median fly) per world"); ax[1,j].set_xlabel("episode"); ax[1,j].set_yscale("symlog"); ax[1,j].legend(fontsize=7)
k=0
for c in CS:
    for f in FD:
        S=np.median(np.array([x["syn_traj"] for x in cell(c,f,"always")]),0); ax[1,2].plot(np.arange(len(S))*4,S,color=cols[k],label=f"upkeep {c:.0e} food {f:.0f}"); k+=1
ax[1,2].set_title("always-reward: synapses per world (does a cheap world let the tumour live?)"); ax[1,2].set_yscale("log"); ax[1,2].set_xlabel("episode"); ax[1,2].legend(fontsize=7)
plt.tight_layout(); plt.savefig("<DATA_ROOT>/economy.png",dpi=110); print("\nsaved economy.png")
