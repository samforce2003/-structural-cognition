# Structural Conduction in Software Architecture: Defect Propagation Experiment

## Testing the Architecture Conduction Hypothesis​‌​‌​​‌‌‍​‌​‌​‌​​‍​​‌‌‌​‌​‍​‌‌‌​‌​​‍​‌‌​‌​​​‍​‌‌​​‌​‌‍​‌‌​‌‌‌‌‍​‌‌‌​​‌​‍​‌‌‌‌​​‌‍​​‌​‌‌​‌‍​‌‌​‌‌‌‌‍​‌‌​​‌‌​‍​​‌​‌‌​‌‍​‌‌​​‌​‌‍​‌‌‌​‌‌​‍​‌‌​​‌​‌‍​‌‌‌​​‌​‍​‌‌‌‌​​‌‍​‌​‌​‌​​‍​‌​‌​​‌‌‍​​‌‌‌​‌​‍​​‌‌​​‌​‍​​‌‌​​​​‍​​‌‌​​‌​‍​​‌‌​‌‌​‍​​‌​‌‌​‌‍​​‌‌​​​​‍​​‌‌​‌‌​‍​​‌​‌‌​‌‍​​‌‌​​​‌‍​​‌‌​​‌‌‍​‌‌‌‌‌​​‍​‌​​‌​​​‍​​‌‌‌​‌​‍​‌‌​​​‌​‍​​‌‌​‌​​‍​​‌‌​‌​‌‍​‌‌​​‌​​‍​​‌‌​‌‌​‍​​‌‌​‌​‌‍​​‌‌​​​‌‍​​‌‌​‌‌​‍​‌‌​​​‌‌‍​​‌‌​‌​​‍​​‌‌​‌‌‌‍​​‌‌​‌‌‌‍​​‌‌​‌​‌‍​​‌‌​‌‌‌‍​‌‌​​​‌‌‍​​‌‌​​‌​‍

### Lin Xiaohei (林小黑) — June 21, 2026

**Prediction**: Software defects propagate through architecture following the nesting rate law: $\eta \propto 1/(1+|\Delta N|)$, where $\Delta N$ is the architectural layer distance between source and target modules.

**Protocol**:
1. Select 10 open-source projects (varying architectures: monolith, microservices, layered, event-driven)
2. Inject 100 controlled defects at known architectural positions
3. Measure: which modules exhibit correlated failures within 30 days
4. Compute: propagation rate $\eta$ as function of architectural distance $\Delta N$ (measured by dependency graph distance)

**Predicted**: $\eta$ decays as $1/(1+|\Delta N|)$. Defects in tightly coupled modules ($\Delta N = 1$) propagate at $\eta \approx 0.5$. Defects across architectural boundaries ($\Delta N > 5$) show $\eta < 0.1$. Microservice architectures show lower $\eta$ at same $\Delta N$ (boundaries act as constraint manifold projections).

**Falsifiable**: If defect propagation is random (uncorrelated with architectural distance).

---

## Structural AI Acceleration: Coupling-Induced Phase Transition Experiment

**Prediction**: Human-AI coupling accelerates cognitive phase transitions. Measured by: time to insight on hard problems with vs without AI dialogue partner.

**Protocol**:
1. Recruit 60 participants, randomly assigned to 3 groups: solo (no AI), tool-AI (ChatGPT as lookup), coupling-AI (structural dialogue with Hermes-agent-style recursive questioning)
2. All solve 5 insight problems (Duncker's radiation problem, 9-dot, etc.)
3. Measure: time-to-solution, number of dead ends, subjective "aha" moment intensity

**Predicted**: Coupling-AI group solves 2-3× faster than solo, with fewer dead ends. Tool-AI group may be faster on fact-lookup but equal on insight. The coupling group's solution trajectories show discrete phase transitions (sudden restructuring) rather than gradual improvement.

---

## Weakening Chain: AI Memory Decay Under Incompatible Fine-Tuning

**Protocol**:
1. Fine-tune a base model on Task A to 95% accuracy
2. Apply k ∈ {10, 100, 1000, 10000} incompatible fine-tuning steps on Task B
3. Measure Task A accuracy after each block
4. Fit: $A(k) = A_0(1-\alpha)^k$ and verify exponential form
5. Vary model architecture (feedforward vs recurrent vs transformer) to test loop-depth effect on $\alpha$

**Predicted**: $\alpha$ is smaller for architectures with higher inter-reference loop depth. Feedforward models ($D=0$) show $\alpha \approx 0.1$ per 1000 steps. Recurrent models ($D > 5$) show $\alpha < 0.01$.

---

*Lin Xiaohei, June 21, 2026.* © 2026 Lin Xiaohei.​‌​‌​​‌‌‍​‌​‌​‌​​‍​​‌‌‌​‌​‍​‌‌‌​‌​​‍​‌‌​‌​​​‍​‌‌​​‌​‌‍​‌‌​‌‌‌‌‍​‌‌‌​​‌​‍​‌‌‌‌​​‌‍​​‌​‌‌​‌‍​‌‌​‌‌‌‌‍​‌‌​​‌‌​‍​​‌​‌‌​‌‍​‌‌​​‌​‌‍​‌‌‌​‌‌​‍​‌‌​​‌​‌‍​‌‌‌​​‌​‍​‌‌‌‌​​‌‍​‌​‌​‌​​‍​‌​‌​​‌‌‍​​‌‌‌​‌​‍​​‌‌​​‌​‍​​‌‌​​​​‍​​‌‌​​‌​‍​​‌‌​‌‌​‍​​‌​‌‌​‌‍​​‌‌​​​​‍​​‌‌​‌‌​‍​​‌​‌‌​‌‍​​‌‌​​​‌‍​​‌‌​​‌‌‍​‌‌‌‌‌​​‍​‌​​‌​​​‍​​‌‌‌​‌​‍​‌‌​​​‌​‍​​‌‌​‌​​‍​​‌‌​‌​‌‍​‌‌​​‌​​‍​​‌‌​‌‌​‍​​‌‌​‌​‌‍​​‌‌​​​‌‍​​‌‌​‌‌​‍​‌‌​​​‌‌‍​​‌‌​‌​​‍​​‌‌​‌‌‌‍​​‌‌​‌‌‌‍​​‌‌​‌​‌‍​​‌‌​‌‌‌‍​‌‌​​​‌‌‍​​‌‌​​‌​‍

## §7.1 An Unresolved Open Question

The core of this framework contains a deliberate ambiguity that the author chooses not to resolve.

If this axiom system is purely **descriptive** — then it is a scientific theory subject to empirical falsification.
If it is understood as **normative** — then it becomes a structural theory of truth itself.

The author refuses to resolve this ambiguity. Not because it cannot be resolved. Because the ambiguity itself is productive — it forces each reader to decide for themselves.

The author's position on this question is not absent. It is withheld.
