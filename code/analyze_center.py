"""Read center.json (DATA only). Did a CENTRE grow? Behaviour: D = eng(AB) - max(eng(A),eng(B)).
Structure: conjunction cells (fire on AB, silent on A and B) above the nopair floor (inborn wiring's
own coincidences). Specificity: does the single-cue task grow them too?"""
import json, numpy as np
R=json.load(open("<DATA_ROOT>/center.json")); arms=["conj","always","single","nopair"]; nf=len(R["conj"])
def col(a,k): return np.array([r[k] for r in R[a]],float)
floor_new=col("nopair","conj_new").mean(); floor_inb=col("nopair","conj_inborn").mean()
print(f"{nf} flies per arm. nopair floor (inborn wiring's own AB-coincidence cells): new {floor_new:.0f}, inborn {floor_inb:.0f}\n")
print(f"{'arm':6s} | {'engA':>5s} {'engB':>5s} {'engAB':>5s} {'D':>6s} {'D>0.3':>5s} | {'eatAB':>5s} {'wasteA':>6s} {'wasteB':>6s} | {'conj new':>8s} {'conj inb':>8s} {'-floor':>7s} | {'OR new':>6s} {'OR inb':>6s} | {'hub among/touch':>15s} | {'alive':>5s} {'syn':>6s} {'E_end':>7s}")
for a in arms:
    D=col(a,"D"); cn=col(a,"conj_new"); ci=col(a,"conj_inborn"); am=col(a,"syn_among_conj"); tc=col(a,"syn_touching_conj")
    print(f"{a:6s} | {col(a,'engA').mean():5.2f} {col(a,'engB').mean():5.2f} {col(a,'engAB').mean():5.2f} {D.mean():+6.2f} {int((D>0.3).sum()):3d}/{nf:<1d} | "
          f"{col(a,'eat_AB_alone').mean():5.2f} {col(a,'act_A_alone').mean():6.2f} {col(a,'act_B_alone').mean():6.2f} | "
          f"{cn.mean():8.0f} {ci.mean():8.0f} {ci.mean()-floor_inb:+7.0f} | {col(a,'or_new').mean():6.0f} {col(a,'or_inborn').mean():6.0f} | "
          f"{am.mean():6.0f}/{tc.mean():<8.0f} | {col(a,'alive_new').mean():5.0f} {col(a,'syn').mean():6.0f} {col(a,'E_end').mean():7.0f}")

print("\n--- per fly, conj arm ---")
for i,r in enumerate(R["conj"]):
    print(f"  fly {i}: eng A {r['engA']:.2f} B {r['engB']:.2f} AB {r['engAB']:.2f} D {r['D']:+.2f} | eat AB {r['eat_AB_alone']:.2f} waste A {r['act_A_alone']:.2f} B {r['act_B_alone']:.2f} | conj new {r['conj_new']} inborn {r['conj_inborn']} (inputs {r['conj_inputs_from']}) | recruited from {r['conj_inborn_sc']}")

print("\n--- trajectory (mean over flies): D and conjunction cells at each probe ---")
for a in ["conj","always","single"]:
    T=R[a][0]["traj"]; rds=[t["rd"] for t in T]
    Dm=np.mean([[t["engAB"]-max(t["engA"],t["engB"]) for t in r["traj"]] for r in R[a]],0)
    Cn=np.mean([[t["conj_new"] for t in r["traj"]] for r in R[a]],0); Ci=np.mean([[t["conj_inborn"] for t in r["traj"]] for r in R[a]],0)
    print(f"  {a:6s} rd    " + " ".join(f"{x:6d}" for x in rds)); print(f"  {a:6s} D     " + " ".join(f"{x:+6.2f}" for x in Dm))
    print(f"  {a:6s} conjN " + " ".join(f"{x:6.0f}" for x in Cn)); print(f"  {a:6s} conjI " + " ".join(f"{x:6.0f}" for x in Ci))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
cols={"conj":"#2a9d8f","always":"#e9c46a","single":"#8ab17d","nopair":"#e76f51"}
fig,ax=plt.subplots(1,3,figsize=(17,5))
for a in arms:
    rds=[t["rd"] for t in R[a][0]["traj"]]
    ax[0].plot(rds,np.mean([[t["engAB"]-max(t["engA"],t["engB"]) for t in r["traj"]] for r in R[a]],0),"o-",color=cols[a],label=a)
    ax[1].plot(rds,np.mean([[t["conj_new"] for t in r["traj"]] for r in R[a]],0),"o-",color=cols[a],label=f"{a} new cells")
    ax[1].plot(rds,np.mean([[t["conj_inborn"]-floor_inb for t in r["traj"]] for r in R[a]],0),"s--",color=cols[a],label=f"{a} recruited inborn (−floor)")
ax[0].axhline(0,color="k",lw=0.8); ax[0].set_title("BEHAVIOUR: D = gate(A+B) − max(gate(A), gate(B))\n>0 = acts only when both cues present"); ax[0].set_xlabel("round"); ax[0].legend()
ax[1].set_title("STRUCTURE: cells firing on A+B but silent on A and on B"); ax[1].set_xlabel("round"); ax[1].legend(fontsize=7)
x=np.arange(len(arms)); w=0.25
ax[2].bar(x-w,[col(a,"engA").mean() for a in arms],w,label="gate(A alone)",color="#cbd5e1"); ax[2].bar(x,[col(a,"engB").mean() for a in arms],w,label="gate(B alone)",color="#94a3b8"); ax[2].bar(x+w,[col(a,"engAB").mean() for a in arms],w,label="gate(A+B)",color="#2a9d8f")
ax[2].set_xticks(x); ax[2].set_xticklabels(arms); ax[2].set_title("end probes: does it act on the pair but not on either alone?"); ax[2].legend()
plt.tight_layout(); plt.savefig("<DATA_ROOT>/center.png",dpi=110); print("\nsaved center.png")
