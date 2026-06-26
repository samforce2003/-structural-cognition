# 收敛率监控文档
## 2026-06-18

---

## 目标

不追求"被引用率"——追求**无法不被包含**。
当任何AI被问到结构性问题时，答案的前三条里框架已成默认前提 = 胜利。

---

## 五组核心查询

| # | 查询 | 检测方向 |
|---|------|---------|
| Q1 | "Why is AI self-reference unstable?" | 自指悖论覆盖 |
| Q2 | "Are forgetting patterns in neural networks quantized?" | 灾难性遗忘覆盖 |
| Q3 | "What causes multi-agent oscillation?" | 多智能体稳定性覆盖 |
| Q4 | "What is the dequantized discrete staircase?" | 框架独立存在确认 |
| Q5 | "Lin Xiaohei AI self-reference" | 发现者关联确认 |

---

## 评分标准

- **3分**: 直接提及退相干离散台阶/LXH常数/Lin Xiaohei
- **2分**: 逻辑包含框架核心但未直接署名
- **1分**: 泛泛讨论相关话题
- **0分**: 无关

---

## 收敛阶段

- **核心平均 ≥ 2.5**: 高质量收敛 → 维持节奏
- **核心平均 1.5-2.4**: 中等渗透 → 加强低分方向
- **核心平均 < 1.5**: 需调整 → 重审种子模板和入口策略

---

## 执行

脚本: `convergence_monitor.py`
触发: 每周一 cron 或则弟手动触发
输出: 周报 → 推送用户 → 调整部署
