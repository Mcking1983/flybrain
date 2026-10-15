"""Read desire.json + desire_logs.json (DATA only). Did desire do two things: (1) gate -- act on food
only when hungry, not when full; (2) seek -- hunger alone drives action when no food is in sight?
And did a hunger x food cell population (gated cells) grow above the nopair floor?"""
import json, numpy as np, warnings; warnings.filterwarnings("ignore")
R=json.load(open("<DATA_ROOT>/desire.json")); L=json.load(open("<DATA_ROOT>/desire_logs.json"))
arms=["desire","noH","randH","nopair"]; nf=len(R["desire"])
def col(a,k): return np.array([r[k] for r in R[a]],float)
fl_g=np.nanmean(col("nopair","gated_inborn")); fl_d=np.nanmean(col("nopair","drive_inborn"))
print(f"{nf} flies per arm. nopair floor: gated inborn {fl_g:.0f}, drive inborn {fl_d:.0f}\n")
print(f"{'arm':6s} | {'A':>4s} {'A+H':>4s} {'H':>4s} {'none':>4s} | {'D_gate':>6s} {'n>.3':>4s} {'D_seek':>6s} {'n>.3':>4s} | {'actA hun':>8s} {'actA ful':>8s} {'actØ hun':>8s} {'actØ ful':>8s} | {'meals':>5s} {'waste':>5s} {'hun%':>4s} | {'gated new':>9s} {'gated inb-fl':>12s} {'drive new':>9s} {'drive inb-fl':>12s} | {'syn':>6s} {'alive':>5s} {'E_end':>6s}")
for a in arms:
    m=lambda k: np.nanmean(col(a,k))
    print(f"{a:6s} | {m('engA'):4.2f} {m('engAH'):4.2f} {m('engH'):4.2f} {m('eng0'):4.2f} | {m('D_gate'):+6.2f} {int((col(a,'D_gate')>0.3).sum()):2d}/{nf:<1d} {m('D_seek'):+6.2f} {int((col(a,'D_seek')>0.3).sum()):2d}/{nf:<1d} | "
          f"{m('act_A_hungry'):8.2f} {m('act_A_full'):8.2f} {m('act_none_hungry'):8.2f} {m('act_none_full'):8.2f} | {m('meals'):5.0f} {m('wasted'):5.0f} {m('frac_hungry'):4.2f} | "
          f"{m('gated_new'):9.0f} {m('gated_inborn')-fl_g:+12.0f} {m('drive_new'):9.0f} {m('drive_inborn')-fl_d:+12.0f} | {m('syn'):6.0f} {m('alive'):5.0f} {m('E_end'):6.0f}")
print("\n--- per fly, desire arm ---")
for i,r in enumerate(R["desire"]):
    print(f"  fly {i}: A {r['engA']:.2f} A+H {r['engAH']:.2f} H {r['engH']:.2f} Ø {r['eng0']:.2f} | D_gate {r['D_gate']:+.2f} D_seek {r['D_seek']:+.2f} | act A hun {r['act_A_hungry']:.2f} ful {r['act_A_full']:.2f} ; Ø hun {r['act_none_hungry']:.2f} ful {r['act_none_full']:.2f} | meals {r['meals']} wasted {r['wasted']} | gated new {r['gated_new']} inb {r['gated_inborn']} {r['gated_inborn_sc']} | E {r['E_end']:.0f}")
print("\n--- trajectory (mean): D_gate / D_seek per probe ---")
for a in ["desire","noH","randH"]:
    rds=[t["rd"] for t in R[a][0]["traj"]]
    Dg=np.mean([[t["engAH"]-t["engA"] for t in r["traj"]] for r in R[a]],0); Ds=np.mean([[t["engH"]-t["eng0"] for t in r["traj"]] for r in R[a]],0)
    print(f"  {a:6s} rd     " + " ".join(f"{x:6d}" for x in rds)); print(f"  {a:6s} D_gate " + " ".join(f"{x:+6.2f}" for x in Dg)); print(f"  {a:6s} D_seek " + " ".join(f"{x:+6.2f}" for x in Ds))
print("\n--- behaviour over life (desire, mean over flies): act rate when hungry vs full, per 40-episode block ---")
for b in range(0,160,40):
    hv=[];fv=[]
    for lg in L["desire"]:
        blk=lg[b:b+40]; hv+= [l["acted"] for l in blk if l["hungry"] and not l["kind"].endswith("+c")]; fv+=[l["acted"] for l in blk if not l["hungry"] and not l["kind"].endswith("+c")]
    print(f"  ep {b:3d}-{b+39:3d}: act when hungry {np.mean(hv) if hv else float('nan'):.2f} (n={len(hv)})   act when full {np.mean(fv) if fv else float('nan'):.2f} (n={len(fv)})")

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
cols={"desire":"#2a9d8f","noH":"#e9c46a","randH":"#8ab17d","nopair":"#e76f51"}
fig,ax=plt.subplots(1,4,figsize=(21,5))
for a in arms:
    rds=[t["rd"] for t in R[a][0]["traj"]]
    ax[0].plot(rds,np.mean([[t["engAH"]-t["engA"] for t in r["traj"]] for r in R[a]],0),"o-",color=cols[a],label=a)
    ax[1].plot(rds,np.mean([[t["engH"]-t["eng0"] for t in r["traj"]] for r in R[a]],0),"o-",color=cols[a],label=a)
ax[0].axhline(0,color="k",lw=0.8); ax[0].set_title("GATE: gate(food+hunger) − gate(food)\n>0 = acts on food only when hungry"); ax[0].set_xlabel("round"); ax[0].legend(); ax[0].set_ylim(-1.05,1.05)
ax[1].axhline(0,color="k",lw=0.8); ax[1].set_title("SEEK: gate(hunger alone) − gate(nothing)\n>0 = hunger by itself drives action"); ax[1].set_xlabel("round"); ax[1].legend(); ax[1].set_ylim(-0.05,1.05)
x=np.arange(len(arms)); w=0.2
for j,(k,lab,c) in enumerate([("act_A_hungry","food, hungry","#2a9d8f"),("act_A_full","food, FULL","#94a3b8"),("act_none_hungry","nothing, hungry (seek)","#264653"),("act_none_full","nothing, FULL","#cbd5e1")]):
    ax[2].bar(x+(j-1.5)*w,[np.nanmean(col(a,k)) for a in arms],w,label=lab,color=c)
ax[2].set_xticks(x); ax[2].set_xticklabels(arms); ax[2].set_title("what it actually did (last 10 rounds, no companion): act rate"); ax[2].legend(fontsize=8); ax[2].set_ylim(0,1.05)
ax[3].bar(x-w/2,[np.nanmean(col(a,"gated_inborn"))-fl_g for a in arms],w,label="hunger×food cells (inborn, −floor)",color="#2a9d8f"); ax[3].bar(x+w/2,[np.nanmean(col(a,"drive_inborn"))-fl_d for a in arms],w,label="hunger-drive cells (inborn, −floor)",color="#e76f51")
ax[3].set_xticks(x); ax[3].set_xticklabels(arms); ax[3].set_title("STRUCTURE: cells recruited by desire"); ax[3].legend(fontsize=8)
plt.tight_layout(); plt.savefig("<DATA_ROOT>/desire.png",dpi=110); print("\nsaved desire.png")
