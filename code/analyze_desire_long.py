"""Read desire_long.json + desire_long_logs.json (DATA only). A long life with desire: what CHANGES
over 600 episodes? Gating, seeking, structure (lean? consolidating?), recruited cells, economics."""
import json, numpy as np, warnings; warnings.filterwarnings("ignore")
R=json.load(open("<DATA_ROOT>/desire_long.json")); L=json.load(open("<DATA_ROOT>/desire_long_logs.json"))
arms=[a for a in ["desire","noH"] if a in R]; nf=len(R["desire"]); EP=len(L["desire"][0])
print(f"{nf} flies per arm, {EP} episodes\n")
def traj(a,f): return np.mean([[fn(t) for t in r["traj"]] for r in R[a]],0)
rds=[t["rd"] for t in R["desire"][0]["traj"]]
print("=== PROBES over life (mean of flies), desire arm ===")
print(f"{'round':>6s} {'gate(A)':>7s} {'gate(A+H)':>9s} {'gate(H)':>7s} {'D_gate':>6s} {'D_seek':>6s} | {'gated inb':>9s} {'drive inb':>9s} {'gated new':>9s} {'drive new':>9s}")
for i,rd in enumerate(rds):
    if rd%10 and rd!=rds[-1]: continue
    g=lambda k: np.mean([r["traj"][i][k] for r in R["desire"]])
    print(f"{rd:6d} {g('engA'):7.2f} {g('engAH'):9.2f} {g('engH'):7.2f} {g('engAH')-g('engA'):+6.2f} {g('engH')-g('eng0'):+6.2f} | {g('gated_inborn'):9.0f} {g('drive_inborn'):9.0f} {g('gated_new'):9.0f} {g('drive_new'):9.0f}")
print("\n=== BEHAVIOUR + STRUCTURE + ECONOMY per 100-episode block (desire arm; no-companion episodes for act rates) ===")
print(f"{'episodes':>10s} | {'act food hun':>12s} {'act food FULL':>13s} {'act Ø hun(seek)':>15s} {'act Ø FULL':>10s} | {'meals':>5s} {'wasted':>6s} {'hungry%':>7s} | {'syn':>6s} {'cold':>6s} {'alive':>5s} | {'E end':>7s}")
for b in range(0,EP,100):
    sel=lambda f: [l for lg in L["desire"] for l in lg[b:b+100] if f(l)]
    ah=sel(lambda l:l["kind"]=="A" and l["hungry"]); af=sel(lambda l:l["kind"]=="A" and not l["hungry"]); nh=sel(lambda l:l["kind"]=="none" and l["hungry"]); nfu=sel(lambda l:l["kind"]=="none" and not l["hungry"])
    allb=sel(lambda l:True); m=lambda v:(np.mean([x["acted"] for x in v]) if v else float("nan"))
    print(f"{b:4d}-{min(b+99,EP-1):4d} | {m(ah):12.2f} {m(af):13.2f} {m(nh):15.2f} {m(nfu):10.2f} | {sum(x['got'] for x in allb)/nf:5.0f} {sum(1 for x in allb if x['acted'] and not x['hungry'])/nf:6.0f} {np.mean([x['hungry'] for x in allb]):7.2f} | {np.mean([lg[min(b+99,EP-1)]['syn'] for lg in L['desire']]):6.0f} {np.mean([r['cold'] for r in R['desire']]) if b+100>=EP else float('nan'):6.0f} {np.mean([lg[min(b+99,EP-1)]['alive'] for lg in L['desire']]):5.0f} | {np.mean([lg[min(b+99,EP-1)]['E'] for lg in L['desire']]):7.0f}")
print("\n=== end of life, per fly (desire) ===")
for i,r in enumerate(R["desire"]):
    print(f"  fly {i}: D_gate {r['D_gate']:+.2f} D_seek {r['D_seek']:+.2f} | act food hun {r['act_A_hungry']:.2f} FULL {r['act_A_full']:.2f} ; Ø hun {r['act_none_hungry']:.2f} FULL {r['act_none_full']:.2f} | meals {r['meals']} wasted {r['wasted']} | syn {r['syn']} cold {r['cold']} alive {r['alive']} born {r['born']} | gated inb {r['gated_inborn']} drive inb {r['drive_inborn']} | E {r['E_end']:.0f}")
if "noH" in R:
    print("\n=== noH (null) end of life ===")
    m=lambda k: np.nanmean([r[k] for r in R["noH"]])
    print(f"  D_gate {m('D_gate'):+.2f} D_seek {m('D_seek'):+.2f} | act food hun {m('act_A_hungry'):.2f} FULL {m('act_A_full'):.2f} ; Ø hun {m('act_none_hungry'):.2f} | meals {m('meals'):.0f} wasted {m('wasted'):.0f} | syn {m('syn'):.0f} cold {m('cold'):.0f} | E {m('E_end'):.0f}")

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,ax=plt.subplots(2,3,figsize=(19,9)); c={"desire":"#2a9d8f","noH":"#e9c46a"}
for a in arms:
    r0=[t["rd"] for t in R[a][0]["traj"]]
    ax[0,0].plot(r0,np.mean([[t["engAH"]-t["engA"] for t in r["traj"]] for r in R[a]],0),"-",color=c[a],label=f"{a} D_gate"); ax[0,0].plot(r0,np.mean([[t["engH"]-t["eng0"] for t in r["traj"]] for r in R[a]],0),"--",color=c[a],label=f"{a} D_seek")
    ax[0,1].plot(r0,np.mean([[t["drive_inborn"] for t in r["traj"]] for r in R[a]],0),"-",color=c[a],label=f"{a} hunger-drive cells"); ax[0,1].plot(r0,np.mean([[t["gated_inborn"] for t in r["traj"]] for r in R[a]],0),"--",color=c[a],label=f"{a} hunger×food cells")
    S=np.array([[l["syn"] for l in lg] for lg in L[a]]); Al=np.array([[l["alive"] for l in lg] for lg in L[a]]); E=np.array([[l["E"] for l in lg] for lg in L[a]])
    ax[0,2].plot(np.median(S,0),color=c[a],label=f"{a} synapses"); ax[1,0].plot(np.median(Al,0),color=c[a],label=f"{a} new cells alive"); ax[1,2].plot(np.median(E,0),color=c[a],label=a)
# behaviour per 50-ep block, desire
xs=[];ah=[];af=[];nh=[]
for b in range(0,EP,50):
    sel=lambda f: [l["acted"] for lg in L["desire"] for l in lg[b:b+50] if f(l)]
    xs.append(b+25); ah.append(np.mean(sel(lambda l:l["kind"]=="A" and l["hungry"]) or [np.nan])); af.append(np.mean(sel(lambda l:l["kind"]=="A" and not l["hungry"]) or [np.nan])); nh.append(np.mean(sel(lambda l:l["kind"]=="none" and l["hungry"]) or [np.nan]))
ax[1,1].plot(xs,ah,"o-",color="#2a9d8f",label="food seen, hungry"); ax[1,1].plot(xs,af,"o-",color="#94a3b8",label="food seen, FULL"); ax[1,1].plot(xs,nh,"o-",color="#264653",label="nothing seen, hungry (seek)")
ax[0,0].axhline(0,color="k",lw=0.8); ax[0,0].set_title("gate & seek over a long life"); ax[0,0].set_xlabel("round"); ax[0,0].legend(fontsize=8); ax[0,0].set_ylim(-0.3,1.05)
ax[0,1].set_title("recruited inborn cells (raw counts)"); ax[0,1].set_xlabel("round"); ax[0,1].legend(fontsize=8)
ax[0,2].set_title("grown synapses (median fly)"); ax[0,2].set_xlabel("episode"); ax[0,2].legend(fontsize=8)
ax[1,0].set_title("new cells alive (median fly)"); ax[1,0].set_xlabel("episode"); ax[1,0].legend(fontsize=8)
ax[1,1].set_title("desire: act rate per 50 episodes (no companion)"); ax[1,1].set_xlabel("episode"); ax[1,1].legend(fontsize=8); ax[1,1].set_ylim(-0.05,1.05)
ax[1,2].set_title("energy (median fly; world upkeep 3e-4, meal 6)"); ax[1,2].axhline(0,color="k",lw=0.8,ls="--"); ax[1,2].set_xlabel("episode"); ax[1,2].legend(fontsize=8)
plt.tight_layout(); plt.savefig("<DATA_ROOT>/desire_long.png",dpi=110); print("\nsaved desire_long.png")
