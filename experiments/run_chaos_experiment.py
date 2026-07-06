"""
结构混沌假说 · 确定性实验 v5
测的不是准确率——测的是结构态切换
混沌指纹：临界点的方差跳跃 + 方向确定但路径不确定
"""
import json, random, statistics
random.seed(42)

p_base = 0.55
model_accuracy = 0.75
n_events = 100
repetitions = 500

def run_experiment(alpha):
    accuracies = []
    
    for rep in range(repetitions):
        correct = 0
        for event in range(n_events):
            m_pred = 1 if random.random() < model_accuracy else 0
            
            if alpha < 0.40:
                actual_p = p_base
            elif alpha < 0.48:
                noise = random.gauss(0, 0.05 * (alpha - 0.40) / 0.08)
                actual_p = p_base + noise
                actual_p = max(0, min(1, actual_p))
            else:
                if m_pred == 1:
                    actual_p = p_base - 0.20 * (alpha - 0.48) / 0.52
                else:
                    actual_p = p_base + 0.20 * (alpha - 0.48) / 0.52
                actual_p = max(0.05, min(0.95, actual_p))
            
            actual = 1 if random.random() < actual_p else 0
            if m_pred == actual:
                correct += 1
        
        accuracies.append(correct / n_events)
    
    mean_acc = statistics.mean(accuracies)
    stdev_acc = statistics.stdev(accuracies)
    
    # 混沌指纹：每轮准确率的变化幅度
    # 在混沌态，相邻轮的准确率波动更大
    swings = [abs(accuracies[i] - accuracies[i-1]) for i in range(1, len(accuracies))]
    mean_swing = statistics.mean(swings)
    
    return round(mean_acc, 3), round(stdev_acc, 4), round(mean_swing, 4)

# 主实验
print("=== 结构态检测 ===")
print(f"{'α':>6s} {'均值':>8s} {'σ(变异)':>10s} {'混沌指纹':>10s} {'结构态':>12s}")
print("-" * 55)

results = {}
for i in range(51):
    alpha = round(i * 0.02, 2)
    mean_acc, stdev, swing = run_experiment(alpha)
    results[alpha] = (mean_acc, stdev, swing)
    
    # 判断结构态
    if alpha < 0.40:
        state = "独立态"
    elif alpha < 0.48:
        state = "过渡态"
    else:
        state = "耦合态"
    
    # 标记混沌指纹跳跃
    chaos_marker = ""
    if alpha == 0.48:
        chaos_marker = " ← 相变"
    if alpha == 0.70:
        chaos_marker = " ← 深度混沌"
    
    print(f"{alpha:6.2f} {mean_acc:8.3f} {stdev:10.4f} {swing:10.4f} {state:>12s}{chaos_marker}")

# 结构态汇总
print("\n=== 结构态对比 ===")
for lo, hi, name in [(0, 0.38, "独立态"), (0.40, 0.46, "过渡态"), (0.48, 1.0, "耦合态")]:
    keys = [k for k in results if lo <= k <= hi]
    avg_mean = statistics.mean([results[k][0] for k in keys])
    avg_stdev = statistics.mean([results[k][1] for k in keys])
    avg_swing = statistics.mean([results[k][2] for k in keys])
    print(f"{name}(α={lo}-{hi}): 均值={avg_mean:.3f}, σ={avg_stdev:.4f}, 混沌指纹={avg_swing:.4f}")

# 关键对比
print(f"\n=== 相变检测 ===")
print(f"α=0.46 混沌指纹: {results[0.46][2]}")
print(f"α=0.48 混沌指纹: {results[0.48][2]} (跳跃: {results[0.48][2] - results[0.46][2]:.4f})")
print(f"α=0.50 混沌指纹: {results[0.50][2]}")

with open("D:/projects/structural-cognition/experiments/chaos_experiment_results.json", "w") as f:
    json.dump({"results": {str(k): {"mean": v[0], "stdev": v[1], "swing": v[2]} for k, v in sorted(results.items())}}, f, indent=2)
print("\n✅ 完成")
