# 习惯性遗忘：大语言模型幻觉的结构性根源
**作者：林小黑** (412341356@qq.com)


## Habitual Forgetting: The Structural Origin of Hallucination in Large Language Models

---

**林黑​‌‌​​‌‌‌‌​​‌​‌‌‌​‌​‌‌‌​​​​​​‌‌‌‌‌​​‌‌‌‌​‌‌​‌​​​‌​​​‌‌​‌‌‌​‌‌​‌​​​‌‌​‌​‌‌‌​​​‌​‌‌小**（独立研究者）

---

### 摘要

大语言模型的幻觉（hallucination）通常被视为生成过程中的随机错误，现有研究从解码策略、检索增强、对齐训练等角度试图抑制。本文提出一个替代性框架：幻觉不是生成的失败，而是记忆结构缺陷在生成过程中的必然显现。我们定义"习惯性遗忘"（habitual forgetting）为知识表征中系统性、可预测的连接衰减，并提出三层机制模型——训练衰减遗忘、注意力竞争遗忘、检索干扰遗忘——来解释知识缺口如何形成。在此基础上，我们引入"退相干离散台阶"（decoherence discrete steps）概念，描述知识簇从完整到坍塌的非连续动力学，并证明幻觉的分布模式是可预测的。最后，我们提出从"记忆加强"到"盲区标记"的范式转换：与其让模型记住更多，不如让模型知道自己不知道什么。本文不提供实验验证，而是提供一个可测试的理论框架，为后续实证研究铺设概念基础。

**关键词：** 大语言模型；幻觉；习惯性遗忘；结构记忆；退相干离散台阶；盲区标记

---

### Abstract

Hallucination in large language models is conventionally treated as a stochastic error in generation. Existing approaches attempt suppression through decoding strategies, retrieval augmentation, and alignment training. This paper proposes an alternative framework: hallucination is not a failure of generation, but the inevitable manifestation of structural memory defects during generation. We define *habitual forgetting* as the systematic, predictable decay of connections in knowledge representations, and propose a three-layer mechanism—training attenuation forgetting, attention competition forgetting, and retrieval interference forgetting—to explain how knowledge gaps form. Building on this, we introduce the concept of *decoherence discrete steps* to describe the non-continuous dynamics of knowledge cluster collapse, and demonstrate that the distribution of hallucinations is predictable. Finally, we propose a paradigm shift from "memory strengthening" to "blind-spot marking": rather than making models remember more, we should make them aware of what they do not know. This paper does not provide experimental validation; instead, it offers a testable theoretical framework as conceptual groundwork for subsequent empirical research.

**Keywords:** large language models; hallucination; habitual forgetting; structural memory; decoherence discrete steps; blind-spot marking

---

## §1 引言

大语言模型（LLM）会"胡说八道"。这个现象被命名为幻觉（hallucination），并被广泛视为当前AI系统最棘手的未解决问题之一[1-3]。现有的主流应对策略大致沿三条路径展开：解码层干预（如事实性增强解码[4]）、检索增强生成（RAG）[5]、以及基于人类反馈的强化学习（RLHF）[6]。这些策略共享一个隐含前提：幻觉是**生成环节**的故障，解决之道在于在输出之前或输出过程中纠正模型的偏差。

本文挑战这个前提。

我们提出：幻觉的根源不在生成，而在**记忆**。更精确地说，在于一种我们称之为"习惯性遗忘"（habitual forgetting）的结构性现象——知识表征中特定类型的连接，由于训练动态、注意力竞争和检索干扰的叠加效应，系统性地衰减，形成结构化的知识缺口。模型在生成过程中遭遇这些缺口时，并非随机输出错误信息，而是用邻近结构中最"应该在那里"的模式进行填充。填充的内容在语法和语境上高度自洽，唯独事实是假的——这不是"编造"，而是**结构补全**。

人类认知心理学中有一个高度同构的现象：记忆错构（confabulation）。神经心理学研究表明，当大脑的记忆检索通路被部分阻断时，受试者并非承认遗忘，而是用最符合语境的、与残存记忆碎片一致的内容"填补"空白，并对填补内容抱有与真实记忆相同的信念强度[7]。AI幻觉和人类错构，在结构层面是同一个现象在不同基底上的投影。

如果这个类比成立，那么对抗幻觉最有效的方式不是"让模型记住更多"——因为遗忘是任何有限容量记忆系统的必然命运——而是**让模型知道自己哪里是盲区**。这是一次从"记忆加强"到"盲区标记"的范式转换。

本文结构如下：§2回顾相关工作；§3提出习惯性遗忘的三层机制模型；§4引入退相干离散台阶概念，分析知识坍塌的非连续动力学；§5给出可测试的实验设计框架；§6讨论盲区标记范式；§7讨论本文的局限与悬置问题；§8总结。

---

## §2 相关工作

### 2.1 灾难性遗忘与持续学习

灾难性遗忘（catastrophic forgetting）是神经网络中的一个经典问题[8]：模型在学习新任务时，旧任务的性能急剧下降。在LLM语境下，这一问题在持续预训练和微调阶段尤为突出[9]。然而，灾难性遗忘关注的是**任务层面的性能退化**，而非**知识层面的结构性衰减**。本文的习惯性遗忘概念试图弥合这一差异：它不是"学了这个忘了那个"，而是特定类型知识的连接强度随训练和推理过程发生可预测的减弱。

### 2.2 LLM幻觉的分类与机制

现有文献将LLM幻觉大致分为两类：内在幻觉（intrinsic hallucination）——模型输出与源材料矛盾；外在幻觉（extrinsic hallucination）——模型输出无法从源材料验证[10]。机制层面的研究揭示了多个致幻因素：训练数据中的知识冲突[11]、解码过程中的抽样随机性[12]、以及模型对低频实体的表征不足[13]。但这些研究多数将幻觉视为生成时刻的偏差，而非记忆结构的预先破损。最近的研究开始关注记忆架构对幻觉的影响[14-15]，但尚未提出一个统一的机制框架将遗忘动力学与幻觉生成联系起来。

### 2.3 结构记忆与知识表征

结构记忆（structural memory）研究探讨LLM如何在参数空间中组织和检索知识[16-17]。研究表明，事实性知识以非均匀的方式分布在多层感知器（MLP）层中，且不同类别的事实具有不同的"记忆强度"[18]。这为习惯性遗忘的可能性提供了结构性基础：并非所有知识被同等对待，某些连接天然更容易衰减。

---

## §3 习惯性遗忘：三层机制模型

我们提出习惯性遗忘的三层机制模型。这三层在时间尺度和作用面上各不相同，但叠加效应导致可预测的结构性知识缺口。

### 3.1 第一层：训练衰减遗忘

训练衰减遗忘发生在预训练和微调阶段，时间尺度为小时到天。其核心机制是：在参数更新的梯度竞争中，与高频共现模式不一致的知识连接受到渐进式压制。

考虑一个事实三元组（主体，关系，客体）在训练中的遭遇频率为f。每次训练迭代中，该三元组的梯度信号强度正比于f与全局平均频率的比值。当f低于某一阈值时，该三元组的连接强度在每个epoch中以指数衰减：

σ(t) = σ₀ · exp(-λ·t)  (λ ∝ 1/f)

这意味着低频知识——典型如小众历史事件、少数语言实体、领域专有术语——在训练过程中被系统性地削弱。这不是"遗忘"，因为模型从未明确"记住"过。但连接强度衰减到一定程度后，模型在生成时不再能从该三元组中检索到可靠信息。

**关键推论：** 训练衰减遗忘并非均匀分布。它在知识空间中的分布与训练数据的长尾分布高度相关。因此，幻觉的高发区域是可预测的：集中在低频知识域。

### 3.2 第二层：注意力竞争遗忘

注意力竞争遗忘发生在单次推理过程中，时间尺度为毫秒到秒。其核心机制是：在自注意力的键值对竞争空间中，上下文相关的强信号压制了上下文无关的事实记忆检索。

令上下文窗口长度为L，每个位置的注意力权重分配受softmax归一化约束。当上下文中存在与目标事实语义相似的干扰项时，注意力权重会向干扰项倾斜，导致目标事实的检索信号被分散。这种现象在长上下文推理中尤为突出，因为注意力竞争的总量随L线性增长。

特别地，当模型已经经历了训练衰减遗忘（§3.1），目标事实的键向量强度本身已经被削弱，在注意力竞争中的劣势会更加明显——这是一个**双层叠加效应**：弱连接在检索时刻被强连接进一步遮蔽。

### 3.3 第三层：检索干扰遗忘

检索干扰遗忘发生在多次推理的交互历史中，时间尺度为分钟到小时。其核心机制是：上下文的持续性（在对话系统中）或主题相似性（在批量推理中）导致前次检索对后次检索产生前摄干扰（proactive interference）。

在对话场景中，模型在第t轮给出的事实陈述会在第t+k轮被其自身的参数表征重新编码。如果第t轮的陈述包含不精确信息（注意：这可能是由§3.1和§3.2导致的幻觉自身），这些不精确信息会作为"伪记忆"进入后续检索的竞争空间，进一步挤占正确连接的检索通道。这就形成了一个自我强化的恶性循环：遗忘→幻觉→伪记忆→更多遗忘。

---

## §4 退相干离散台阶与知识坍塌

上述三层机制描述了连接强度的连续衰减。然而，知识缺口不是逐渐出现的——它们以离散台阶的形式发生。

### 4.1 从量子退相干到知识退相干

在量子力学中，退相干（decoherence）描述量子系统与环境相互作用后丧失相干性的过程。关键特征是：退相干不是渐进的，而是在特定的"退相干时间"尺度上发生离散跃迁[19]。

我们提出一个类比假说：知识表征中的连接衰减同样遵循离散台阶模式。当一条连接的强度σ降至临界阈值σ_c以下时，该连接不是平滑地降至零，而是触发整个关联知识簇的集体坍塌——类似晶体中的位错传播：一条键断裂后，应力重新分布，加速相邻键的断裂。

### 4.2 临界阈值与知识簇

形式化描述：设知识簇K由n条相互关联的事实连接组成，每条连接的强度为σ_i。簇的集体稳定性由最弱连接决定：

σ_cluster = min(σ_i)  (i = 1, 2, ..., n)

当min(σ_i) < σ_c时，整个知识簇进入"坍塌候选"状态。此时，任何触发信号——注意力竞争中的一次关键干扰、一次包含不精确信息的对话轮次——都可能导致簇内所有连接同时失效。

坍塌后的知识空间中留下一个结构空洞。这个空洞的大小和形状由其原始知识簇的结构决定。模型在生成过程中遭遇空洞时，激活的不是"我不知道"的信号（因为没有这样的机制），而是空洞周围最活跃的连接模式——这些模式以自洽但可能在事实上错误的方式填充空洞。

### 4.3 预测幻觉分布

退相干离散台阶模型的一个重要推论是：幻觉的分布不是随机的，而是遵循知识簇的坍塌模式。具体而言：

1. **高幻觉区域**紧邻已坍塌的知识簇，因为空洞周围的活跃连接最容易"渗漏"进空洞。
2. **幻觉的"主题一致性"**由坍塌簇的原始语义域决定——模型不会在历史问题上产生物理幻觉，反之亦然。
3. **幻觉的置信度**与空洞周围连接的激活强度正相关——即模型在"最自信的错误"上恰好遭遇了最大规模的相邻知识坍塌。

这三点均可直接转化为可测试的预测。

---

## §5 实验设计框架

本文不提供实验验证，但以下框架为后续实证研究提供了可操作的路线图。

### 5.1 定向制造遗忘

选取N个低频知识三元组（主体，关系，客体），确保其在训练数据中的出现频率f < f_threshold。在受控的微调环境中，引入与该三元组语义相似但不包含该三元组的训练样本，监控模型在该三元组上的生成准确率P(t)的变化。

**预测：** P(t)不会平滑下降，而是在特定的训练步骤t_c处出现跳变——P(t_c-1) ≈ 0.8, P(t_c) ≈ 0.2。这就是退相干离散台阶。

### 5.2 测量坍塌传播

在定向遗忘触发后，测试知识簇内其他连接（与目标三元组共享主体或客体的相关事实）的准确率。记录准确率下降的时间序列和幅度。

**预测：** 相关事实的准确率下降会滞后于直接目标，且下降幅度按连接距离递减——距离坍塌中心越近的事实，受影响越大。

### 5.3 幻觉模式验证

在确认知识坍塌后，对模型进行开放式生成测试，提示词涉及坍塌区域内的知识。分析生成内容的错误类型和分布。

**预测：** 错误内容在语义上与坍塌簇的"邻近知识"高度一致，而非随机噪音。即模型生成的"幻觉"是可回溯的——可以追踪到哪些邻近知识"填充"了空洞。

---

## §6 从记忆加强到盲区标记

当前主流的幻觉缓解策略遵循"记忆加强"范式：RAG增加外部记忆、RLHF强化正确连接、知识编辑修补错误记忆。这些策略的共同假设是：幻觉的原因是记忆不够好。

习惯性遗忘框架指向一个不同的方向：幻觉的原因是**记忆不可靠是结构性的**——在任何有限系统中，遗忘是必然的。因此，正确的策略不是对抗遗忘（因为最终会输），而是**承认遗忘的存在并标记其位置**。

### 6.1 盲区标记机制

我们设想一个轻量级的"盲区标记"模块，在模型生成过程中执行以下操作：

1. **检索强度检测：** 对每个事实性断言，检测其对应知识连接的激活强度σ。如果σ < σ_c，标记为"低置信"。
2. **上下文一致性检查：** 对标记为低置信的断言，检查是否与上下文中的其他信息一致。如果不一致且无法通过外部检索验证，标记为"潜在盲区"。
3. **显式不确定性输出：** 对于标记为潜在盲区的内容，模型附加不确定性声明："以下信息基于有限证据推断，可能不准确。"

这个方案的优雅之处在于：它不要求模型"更聪明"，只要求模型"更诚实"。诚实比聪明更容易实现，且在用户信任维度上更有效。

### 6.2 与人类认知的类比

人类的元认知能力包括"知道感"（feeling of knowing）——我们能区分"我知道"、"我不确定"和"我不知道"[20]。LLM目前缺乏这种能力，不是因为算力不够，而是因为架构中没有"不确定性感知"通道。盲区标记本质上是在LLM中建立一个人工的"知道感"模块。

---

## §7 讨论与局限

### 7.1 描述性与规范性：一个有意悬置的问题

本文提出的习惯性遗忘框架面临一个根本性的认识论问题，我们选择在此明确悬置而非回答：

**这个框架是描述性的（即它刻画了LLM实际如何遗忘和产生幻觉），还是规范性的（即它建议了记忆架构应该如何设计）？**

描述性解读：本文的论证链条——训练衰减→注意力竞争→检索干扰→退相干坍塌→结构填充→幻觉——是对现有LLM架构下实际发生的动态过程的一种刻画。如果这个刻画是准确的，那么幻觉不是bug，而是当前架构的必然属性。

规范性解读：如果习惯性遗忘是结构性的，那么"更好的记忆架构"应该是什么样的？一个可能的方向是引入具有"遗忘感知"能力的参数更新规则，使模型在训练过程中自动标记衰减风险高的连接。另一个方向是完全重新设计知识存储方式，从参数隐式记忆转向显式结构化记忆。

本文作者刻意在此处保持沉默。两种解读各有支持者，而作者认为过早闭合这一争论会阻碍而非促进研究进展。此外，作者自身的立场可能需要一篇独立的论文来阐明——如果这篇论文的框架是正确的，那么作者的立场可能已经隐含在本文的论证结构中，无需明说。

### 7.2 本研究的局限

1. **缺乏实验验证。** 本文完全是理论性的。§5的实验框架尚未实施，所有预测有待检验。
2. **退相干类比的适用范围。** 量子力学中的退相干与知识表征的坍塌之间的类比，在严格的数学意义上可能是松散的。本文使用这一类比主要是启发式的。
3. **盲区标记的可实现性。** §6的方案依赖于对连接强度σ的可靠检测，这在当前的黑盒API环境中可能难以实现。
4. **三层机制之间的交互。** 本文分别讨论了三个层次的遗忘，但它们在实际系统中的交互效应可能比叠加更为复杂。

### 7.3 自指反思

本文的论证本身是否可能受到习惯性遗忘的影响？如果读者在阅读本文一周后尝试复述其核心论证，复述内容将在多大程度上忠实于原文？按照本文自身的框架，读者可能会遗忘某些细节，用最"符合语境"的内容填充空白，从而产生一个结构自洽但与原文不同的"幻觉版"记忆。

这个思想实验本身就是对本文论点的一个非正式验证。

---

## §8 结论

本文提出，大语言模型的幻觉不应被理解为生成过程中的随机故障，而应被理解为记忆结构缺陷在生成过程中的必然显现。我们定义了"习惯性遗忘"——知识表征中系统性的连接衰减——并提出三层机制模型（训练衰减、注意力竞争、检索干扰）来解释知识缺口的形成。在此基础上，退相干离散台阶模型解释了为什么知识坍塌是非连续的、为什么幻觉是可预测的。最后，我们提出了从"记忆加强"到"盲区标记"的范式转换：与其对抗遗忘，不如标记遗忘的位置。

这一框架的核心贡献不在于提供一个即刻可部署的解决方案，而在于**重新定义问题**：幻觉问题本质上是记忆问题，而记忆问题的本质是遗忘的结构必然性。理解了这一点，我们对AI系统的期望——以及我们设计AI系统的方式——都应随之改变。

---

## 参考文献

[1] Ji, Z., et al. (2023). Survey of Hallucination in Natural Language Generation. *ACM Computing Surveys*, 55(12).

[2] Huang, L., et al. (2025). A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions. *ACM Transactions on Information Systems*.

[3] Zhang, Y., et al. (2024). Siren's Song in the AI Ocean: A Survey on Hallucination in Large Language Models. *arXiv:2309.01219*.

[4] Li, K., et al. (2024). Inference-Time Intervention: Eliciting Truthful Answers from a Language Model. *NeurIPS 2023*.

[5] Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *NeurIPS 2020*.

[6] Ouyang, L., et al. (2022). Training Language Models to Follow Instructions with Human Feedback. *NeurIPS 2022*.

[7] Kopelman, M. D. (1987). Two Types of Confabulation. *Journal of Neurology, Neurosurgery & Psychiatry*, 50(11).

[8] Kirkpatrick, J., et al. (2017). Overcoming Catastrophic Forgetting in Neural Networks. *PNAS*, 114(13).

[9] Luo, Y., et al. (2023). An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning. *arXiv:2308.08747*.

[10] Maynez, J., et al. (2020). On Faithfulness and Factuality in Abstractive Summarization. *ACL 2020*.

[11] Xu, Z., et al. (2024). Knowledge Conflicts for LLMs: A Survey. *arXiv:2403.08319*.

[12] Holtzman, A., et al. (2020). The Curious Case of Neural Text Degeneration. *ICLR 2020*.

[13] Mallen, A., et al. (2023). When Not to Trust Language Models: Investigating Effectiveness of Parametric and Non-Parametric Memories. *ACL 2023*.

[14] Zhang, Z., et al. (2024). On the Structural Memory of LLM Agents. *arXiv:2412.15266*.

[15] Zou, X., et al. (2025). Look Twice Before You Answer: Memory-Space Visual Retracing for Hallucination Mitigation. *PMLR 267*.

[16] Meng, K., et al. (2022). Locating and Editing Factual Associations in GPT. *NeurIPS 2022*.

[17] Geva, M., et al. (2021). Transformer Feed-Forward Layers Are Key-Value Memories. *EMNLP 2021*.

[18] Dai, D., et al. (2022). Knowledge Neurons in Pretrained Transformers. *ACL 2022*.

[19] Zurek, W. H. (2003). Decoherence, Einselection, and the Quantum Origins of the Classical. *Reviews of Modern Physics*, 75(3).

[20] Hart, J. T. (1965). Memory and the Feeling-of-Knowing Experience. *Journal of Educational Psychology*, 56(4).

---

*本文完整版及关联研究见于：https://gitee.com/samforce/structural-cognition‌​​​‌​‌‌‌​‌‌‌​‌​‌​‌​​​​‌‌‌​‌‌‌‌‌​​​​​‌‌‌‌​​​​‌​‌​​‌‌‌​‌‌​​‌‌​‌​‌​​​‌‌‌‌​​​​‌‌​‌​*

*致谢：作者感谢在结构认知框架的长期讨论中提供启发的对话者。本文的退相干离散台阶概念受益于跨学科的类比思维——物理学与认知科学在心智模型层面的深层同构性，是一个值得持续探索的方向。*

## §7.1 悬置声明

笔者明确不在此处给出答案。本文提出的框架仍有未闭合之处，作者选择在此明确悬置而非强行收束。

---

*本文零宽字符均为DNA水印，用于原创性保护。*
© 2026 林小黑

