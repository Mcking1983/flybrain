"""Read select.json (DATA only -- never imports the experiment) and judge whether the
consequence gate actually SELECTS. Reports: (1) per-arm salient/neutral gate + flooding,
(2) the paired contrast modulated-minus-activity per fly (the clean causal number),
(3) pooled per-target engagement distributions, (4) a trajectory plot."""
import json, numpy as np
R=json.load(open("<DATA_ROOT>/select.json"))
arms=["modulated","activity","scrambled","shuffled"]

def col(a,k): return np.array([r[k] for r in R[a]])
print(f"flies per arm: {len(R['modulated'])}\n")
print(f"{'arm':10s} {'salient':>8s} {'neutral':>8s} {'delta':>8s} {'sel>0.1':>8s} | {'syn':>8s} {'cold':>8s} {'motorSyn':>9s} {'born':>6s} {'dead':>6s}")
for a in arms:
    sal=col(a,"sal_mean"); neu=col(a,"neu_mean"); d=col(a,"delta")
    syn=col(a,"syn"); cold=col(a,"cold"); ms=col(a,"motor_syn"); born=col(a,"born"); dead=col(a,"dead")
    print(f"{a:10s} {sal.mean():8.3f} {neu.mean():8.3f} {d.mean():+8.3f} {int((d>0.1).sum()):5d}/{len(d):<2d} | "
          f"{syn.mean():8.0f} {cold.mean():8.0f} {ms.mean():9.0f} {born.mean():6.0f} {dead.mean():6.0f}")

print("\n--- PAIRED (same fly seed & roles): modulated vs each control, per-fly delta difference ---")
md=col("modulated","delta")
for a in ("activity","scrambled","shuffled"):
    ad=col(a,"delta"); diff=md-ad
    wins=int((diff>0).sum()); ties=int((diff==0).sum())
    # normal-approx t on paired diffs
    t=diff.mean()/(diff.std(ddof=1)/np.sqrt(len(diff))) if diff.std(ddof=1)>0 else float("nan")
    print(f"  modulated - {a:9s}: mean {diff.mean():+.3f}  (mod wins {wins}/{len(diff)}, ties {ties})  t={t:+.2f}")

print("\n--- NEUTRAL suppression (want modulated LOW, activity HIGH) ---")
for a in arms:
    neu=col(a,"neu_mean"); print(f"  {a:10s} neutral gate mean {neu.mean():.3f}")
supp=col("activity","neu_mean")-col("modulated","neu_mean")
print(f"  activity_neutral - modulated_neutral (per fly): mean {supp.mean():+.3f}  (positive = selection pruned neutral)")

print("\n--- POOLED per-target engagement (all targets, all flies) ---")
for a in arms:
    S=[]; Nn=[]
    for r in R[a]:
        for e,role in zip(r["eng_end"],r["roles"]):
            (S if role=="salient" else Nn).append(e)
    S=np.array(S); Nn=np.array(Nn)
    print(f"  {a:10s} salient {S.mean():.3f}+/-{S.std():.3f} (n={len(S)})   neutral {Nn.mean():.3f}+/-{Nn.std():.3f} (n={len(Nn)})   gap {S.mean()-Nn.mean():+.3f}")

# trajectory plot: mean salient vs neutral gate over rounds, modulated vs activity
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,3,figsize=(16,4.5))
for ci,a in enumerate(["modulated","activity"]):
    rounds=None; sal_t=[]; neu_t=[]
    for r in R[a]:
        rr=[p["rd"] for p in r["traj"]]; rounds=rr
        svals=[]; nvals=[]
        for p in r["traj"]:
            s=[e for e,role in zip(p["eng"],r["roles"]) if role=="salient"]; nn=[e for e,role in zip(p["eng"],r["roles"]) if role=="neutral"]
            svals.append(np.mean(s)); nvals.append(np.mean(nn))
        sal_t.append(svals); neu_t.append(nvals)
    sal_t=np.array(sal_t).mean(0); neu_t=np.array(neu_t).mean(0)
    ax[ci].plot(rounds,sal_t,"o-",color="#2a9d8f",label="salient cues (keep)")
    ax[ci].plot(rounds,neu_t,"o-",color="#e76f51",label="neutral cues (prune)")
    ax[ci].set_title(f"{a}: gate opening over training"); ax[ci].set_xlabel("round"); ax[ci].set_ylabel("motor engagement (probe alone)")
    ax[ci].set_ylim(-0.05,1.05); ax[ci].legend()
# flooding bar
ax[2].bar(range(len(arms)),[col(a,"motor_syn").mean() for a in arms],color=["#264653","#e9c46a","#f4a261","#8ab17d"])
ax[2].set_xticks(range(len(arms))); ax[2].set_xticklabels(arms,rotation=20); ax[2].set_title("surviving sensory->motor bridges"); ax[2].set_ylabel("count")
plt.tight_layout(); plt.savefig("<DATA_ROOT>/select.png",dpi=110); print("\nsaved select.png")
