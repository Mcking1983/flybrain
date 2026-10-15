"""Read memory.json (DATA only). How fast does the fly forget with disuse? Does anything cold survive?
Does use-without-reward preserve or inflate? Is relearning faster than first learning (savings)?"""
import json, numpy as np, warnings; warnings.filterwarnings("ignore")
R=json.load(open("<DATA_ROOT>/memory.json")); keys=list(R.keys()); nf=len(R[keys[0]])
print(f"{nf} flies per condition\n")
def m(k,ph,f): return np.nanmean([r[ph][f] for r in R[k]])
print(f"{'gap':10s} | {'seek: before':>12s} {'after':>6s} {'ret%':>5s} {'end':>5s} | {'gate: before':>12s} {'after':>6s} {'end':>5s} | {'cells b->a->e':>16s} {'syn b->a->e':>19s} {'cold b->a->e':>13s} | {'1st rd':>6s} {'relearn rd':>10s} {'savings':>7s}")
for k in keys:
    rs=R[k]; sb,sa,se=m(k,"before","D_seek"),m(k,"after","D_seek"),m(k,"end","D_seek"); gb,ga,ge=m(k,"before","D_gate"),m(k,"after","D_gate"),m(k,"end","D_gate")
    t1=[r["t_first"] for r in rs if r["t_first"]]; t3=[r["t_relearn"] for r in rs if r["t_relearn"]]
    T1=np.mean(t1) if t1 else float("nan"); T3=np.mean(t3) if t3 else float("nan")
    print(f"{k:10s} | {sb:12.2f} {sa:6.2f} {100*sa/max(sb,1e-9):4.0f}% {se:5.2f} | {gb:12.2f} {ga:6.2f} {ge:5.2f} | {m(k,'before','alive'):4.0f}->{m(k,'after','alive'):<4.0f}->{m(k,'end','alive'):<5.0f} {m(k,'before','syn'):6.0f}->{m(k,'after','syn'):<6.0f}->{m(k,'end','syn'):<5.0f} {m(k,'before','cold'):3.0f}->{m(k,'after','cold'):<3.0f}->{m(k,'end','cold'):<4.0f} | {T1:6.1f} {T3:6.1f} ({len(t3)}/{nf}) {T1-T3:+6.1f}")
print("\n--- per fly, full gaps: did ANY cold synapse / protected cell survive the gap? ---")
for k in [x for x in keys if x.startswith("full")]:
    for i,r in enumerate(R[k]):
        print(f"  {k:7s} fly {i}: cold {r['before']['cold']:3d}->{r['after']['cold']:3d}  cells {r['before']['alive']:3d}->{r['after']['alive']:3d}  syn {r['before']['syn']:5d}->{r['after']['syn']:5d}  seek {r['before']['D_seek']:.2f}->{r['after']['D_seek']:.2f}  relearn rd {r['t_relearn']} (first {r['t_first']})")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,3,figsize=(17,5))
fk=[k for k in keys if k.startswith("full")]; gaps=[int(k[4:]) for k in fk]
ret=[m(k,"after","D_seek")/max(m(k,"before","D_seek"),1e-9) for k in fk]; retg=[m(k,"after","D_gate")/max(m(k,"before","D_gate"),1e-9) for k in fk]
ax[0].plot([0]+gaps,[1.0]+ret,"o-",color="#2a9d8f",label="seeking retained (disuse, full)"); ax[0].plot([0]+gaps,[1.0]+retg,"s--",color="#264653",label="gating retained (disuse, full)")
hk=[k for k in keys if k.startswith("hungry")]
for k in hk: ax[0].plot([int(k[6:])],[m(k,"after","D_seek")/max(m(k,"before","D_seek"),1e-9)],"*",ms=16,color="#e76f51",label=f"seeking after {k[6:]} eps hungry, nothing to find")
ax[0].axhline(0,color="k",lw=0.8); ax[0].set_xlabel("gap length (quiet episodes)"); ax[0].set_ylabel("after / before"); ax[0].set_title("FORGETTING CURVE"); ax[0].legend(fontsize=8)
x=np.arange(len(keys)); w=0.27
ax[1].bar(x-w,[m(k,"before","alive") for k in keys],w,label="new cells before gap",color="#cbd5e1"); ax[1].bar(x,[m(k,"after","alive") for k in keys],w,label="after gap",color="#2a9d8f"); ax[1].bar(x+w,[m(k,"after","cold") for k in keys],w,label="cold synapses after gap",color="#e9c46a")
ax[1].set_xticks(x); ax[1].set_xticklabels(keys,rotation=20); ax[1].set_title("WHAT SURVIVES THE GAP"); ax[1].legend(fontsize=8); ax[1].set_yscale("symlog")
t1=[np.nanmean([r["t_first"] for r in R[k] if r["t_first"]] or [np.nan]) for k in keys]; t3=[np.nanmean([r["t_relearn"] for r in R[k] if r["t_relearn"]] or [np.nan]) for k in keys]
ax[2].bar(x-w/2,t1,w,label="rounds to learn seeking, 1st time",color="#94a3b8"); ax[2].bar(x+w/2,t3,w,label="rounds to relearn after gap",color="#2a9d8f")
ax[2].set_xticks(x); ax[2].set_xticklabels(keys,rotation=20); ax[2].set_title("SAVINGS: is relearning faster? (a latent trace would show here)"); ax[2].legend(fontsize=8)
plt.tight_layout(); plt.savefig("<DATA_ROOT>/memory.png",dpi=110); print("\nsaved memory.png")
