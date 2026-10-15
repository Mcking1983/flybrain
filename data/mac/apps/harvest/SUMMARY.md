# Mac 果蝇训练臂收工记录（2026-10-04）

三个 plist 已从 `~/Library/LaunchAgents/` 移到 `/Users/boxiang/flybrain/plists-retired/`（含 `com.flybrain.macswarm.plist.bak-4pop`），重启后不会再自动拉起。
要恢复训练：把 plist 移回 LaunchAgents，再 `launchctl bootstrap gui/$(id -u) <plist>`。
`~/Library/LaunchAgents/` 里还剩 5 个休眠的 flybrain plist（均未加载）：`bridge`、`feeder`、`macarm`、`showcase`、`swarm`。
六个监视器（health / pace / bounds / contrast / divarm / probe tail）同时停掉。

## 最终账目

| | gpu_300 控制臂 | gpu_313 原参数框 | gpu_314 加宽参数框 |
|---|---|---|---|
| 配置 | llm-cap 8, `--teach`, **MOTOR_CONTRAST=0** | llm-cap 18, `MOTOR_CONTRAST=1`, `INHERIT_*=0` | 同上 + `BOUNDS_WIDEN=1` |
| 世代数 | 664 | 224 | 141 |
| 首次 solo>0 | gen 0 | **gen 217** | gen 4 |
| 峰值 solo（满值 144 = 8蝇×18任务） | 144 (gen 506) | 36 (gen 223) | 55 (gen 63) |
| 末代单蝇最好 | 18/18 | 8/18 | 8/18 |
| 末代电机量 | +1.4178 | +0.0930 | +0.0755 |
| 累计 LLM 调用 | 78 | 16,461 | 10,139 |
| 累计 token | 49,554 | 10,429,312 | 6,526,790 |
| 末代学习突触/蝇 | 3,200,000（全部钉在 SYN_CAP） | 478,913–1,881,392 | 365–1,448,748 |

总花费：26,678 次 LLM 调用，17,005,656 token。

## 三条臂各自证明了什么

**gpu_300 的 18/18 是门控失效的产物，不是能力。** 它没有开 `MOTOR_CONTRAST`，`task_rate` 读的是整个电机组的平均发放率（+1.4178），门槛 0.01 恒成立，所以每个任务都判成 solo。8 只蝇的突触全部钉在 SYN_CAP、rate 完全相同（+1.4178 / +1.4177），群体已经收敛成一个个体。这条臂作为"无对比度时门控会全开"的对照是有用的，作为能力指标是无效的。

**gpu_313 证明原参数框能突破，只是慢。** gen 0–216 电机对比度锁在 −0.0192，solo 恒为 0，8 个参数钉在边界。gen 217 一只蝇跳到 +0.0602，solo 立刻出现；gen 223 到 36/144。之前"参数框就是墙"的结论要改成：加宽框把突破提前了约 200 代。

**gpu_314 证明加宽框让门控从 gen 4 起就是活的。** 稳定在 40–55/144，单蝇最多 8/18 个任务白拿。对比度均值 +0.054~+0.068，学习突触从 365 到 144 万，跨度极大 —— 加宽框让参数真正逃逸了。

## token 账单是结构性的

两臂从 gen 0 到收工，每代固定 72 次 LLM 调用、约 47k token，一条平线。
72 = 4 个空白槽 × 18 个任务。幸存者 store 完整，token 花费为 0。
`INHERIT_STORE=0` + `elite=4` + `evolve()` 删除非幸存者的 npz 和 store，导致每代都有 4 只蝇从零重建缓存。
**LLM 的钱全部花在"我们主动扔掉记忆"上，与任务难度无关。**

## 果蝇 + LLM 的可信结论

解法 100% 来自 LLM + `verify()`：gpu_314 slot4 只有 365 个学习突触（图基本空白），照样 180/180 通过。`ok` 这个指标已经饱和，没有信息量。

果蝇唯一可测量的贡献是**门控**：判断"这个任务我能不能不问 LLM 就执行"。在对比度门控下，这个数是单蝇 8/18、群体 40–55/144。

四个候选角色里三个已判死：时序记忆只有 1–2 步（29 种配置）；输入中继 R² 0.91–0.96 等于线性拷贝；叠加线索下通道 margin = 0.0000。

## 保留下来的资产

`apps/harvest/<pop>/`：每臂末代 solo 最高的 2 只蝇的 `.npz` + `_store.json`，加 `genomes.json` 和完整 `evo_ledger.jsonl`。
- gpu_314 slot5：8/18 solo，5,987 个学习突触 —— 图几乎空白也能门控 8 个任务，说明 solo 计数主要由 store 覆盖决定，突触数量不是主因。
- gpu_314 slot6：8/18 solo，738,868 突触。
- gpu_313 slot7：8/18 solo，rate +0.0542。

原始 pop 目录（`apps/gpu_300|313|314/`）未删除，可原地续跑。

## 下一步（未开）

`app_evo.py:429-431` 已内置两种排序键，换适应度是 env 改动：`RANK_KEY=solo`（选择压力从电机对比度换成白拿任务数）+ `INHERIT_STORE=1`（缓存不再每代删一半）。
预测：token/代从 47k 掉向 0，`ok` 保持 180/180，`solo_sum` 从 45 往 144 爬；饱和点就是果蝇的真实天花板。
