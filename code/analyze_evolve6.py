"""Experiment 6 (DATA only; works on partial runs): per arm (ctrl / cost / cost2) x seed: Δ = select - random
probe-set score per generation, population mean synapses / cold, survivors, cost per episode.
Verdict per the pre-registered thresholds: Δ shrink vs ctrl > 30% -> the separation was mostly body size;
< 10% change -> mostly ability. Writes evolve6_final.md and appends it to DISCUSSION when RUN_FINAL=1."""
import json, os, glob, numpy as np, warnings; warnings.filterwarnings("ignore")
D="<DATA_ROOT>"; PREFIX=os.environ.get("PREFIX","evolve6"); ARMS=os.environ.get("ARMS","ctrl,cost,cost2").split(","); SEEDS=[11,23]; L=["select","random"]
TITLE=os.environ.get("TITLE","第 6 个世代实验")
H={}
for a in ARMS:
    for s in SEEDS:
        for l in L:
            f=f"{D}/{PREFIX}_{a}_s{s}_{l}.json"
            if os.path.exists(f): H[(a,s,l)]=json.load(open(f))
if not H: print("no data yet"); raise SystemExit
G=min(len(h) for h in H.values()); print(f"generations available: {G}  ({len(H)}/12 populations)\n")
def m(a,s,l,g,k): return float(np.mean([r[k] for r in H[(a,s,l)][g]["results"]]))
out=[]; P=out.append
P(f"\n---\n\n## {TITLE} · 结果({G} 代 = g0~g{G-1};自动汇总)\n")
P("### ① Δ(被选 − 随机 探针套均分)逐代,三臂对照\n")
P("| 臂 | 种子 | " + " | ".join(f"g{g}" for g in range(G)) + " | 末代 Δ |"); P("|---|---|" + "---|"*G + "---|")
dend={}
for a in ARMS:
    for s in SEEDS:
        if (a,s,"select") in H and (a,s,"random") in H:
            ds=[m(a,s,"select",g,"score")-m(a,s,"random",g,"score") for g in range(G)]; dend[(a,s)]=np.mean(ds[-2:]) if G>=2 else ds[-1]
            P(f"| {a} | {s} | " + " | ".join(f"{d:+.3f}" for d in ds) + f" | {ds[-1]:+.3f} |")
P("\n(末代 Δ 用最后两代均值判缩放,压单代噪声)\n")
P("### ② 群均突触 / 冷突触逐代(被选谱系;括号内随机谱系)\n")
P("| 臂 | 种子 | " + " | ".join(f"g{g}" for g in range(G)) + " |"); P("|---|---|" + "---|"*G)
for a in ARMS:
    for s in SEEDS:
        if (a,s,"select") in H: P(f"| {a} 突触 | {s} | " + " | ".join(f"{m(a,s,'select',g,'syn'):.0f} ({m(a,s,'random',g,'syn'):.0f})" for g in range(G)) + " |")
for a in ARMS:
    for s in SEEDS:
        if (a,s,"select") in H: P(f"| {a} 冷 | {s} | " + " | ".join(f"{m(a,s,'select',g,'cold'):.0f} ({m(a,s,'random',g,'cold'):.0f})" for g in range(G)) + " |")
P("\n### ③ 幸存者 / 每回合成本 / 父母池群均突触(被选谱系;POOL = 能量>0 的个体的群均突触,即真实父母池)\n")
P("| 臂 | 种子 | " + " | ".join(f"g{g}" for g in range(G)) + " |"); P("|---|---|" + "---|"*G)
for a in ARMS:
    for s in SEEDS:
        if (a,s,"select") in H: P(f"| {a} | {s} | " + " | ".join(f"{len(H[(a,s,'select')][g]['survivors'])}/20 · {m(a,s,'select',g,'cost_per_ep'):.2f} · pool {np.mean([H[(a,s,'select')][g]['results'][i]['syn'] for i in H[(a,s,'select')][g]['survivors']]) if H[(a,s,'select')][g]['survivors'] else float('nan'):.0f}" for g in range(G)) + " |")
P("\n### 判词(预登记阈值:Δ 缩 >30% → 主要是体型;变化 <10% → 主要是能力)\n")
for a in [x for x in ARMS if x!="ctrl"]:
    for s in SEEDS:
        if (a,s) in dend and ("ctrl",s) in dend:
            dc,d=dend[("ctrl",s)],dend[(a,s)]; shrink=(dc-d)/abs(dc)*100 if dc else float("nan")
            syn_c=np.mean([m("ctrl",s,"select",g,"syn") for g in range(max(0,G-2),G)]); syn_a=np.mean([m(a,s,"select",g,"syn") for g in range(max(0,G-2),G)])
            syn_drop=(syn_c-syn_a)/syn_c*100 if syn_c else float("nan")
            if syn_drop<30: v="**未决:突触没被压住(↓<30%),操作未咬到,判词不算**"
            else: v="体型为主(突触压住且 Δ 缩 >30%)" if shrink>30 else ("能力为主(突触压住,Δ 变化 <10%)" if abs(shrink)<10 else "中间地带(突触压住,Δ 缩 10~30%)")
            P(f"- **{a} 种子 {s}**:Δ ctrl {dc:+.3f} → {a} {d:+.3f}(缩 {shrink:+.0f}%);被选突触 ctrl {syn_c:.0f} → {syn_a:.0f}({(syn_a-syn_c)/syn_c*100:+.0f}%) → **{v}**")
P("")
md="\n".join(out); print(md); open(f"{D}/{PREFIX}_final.md","w").write(md)
if os.environ.get("RUN_FINAL"): open(f"{D}/DISCUSSION_20260917.md","a").write(md); print("\n(appended to DISCUSSION)")
