# 免拦截投稿邮件模板

## 拦截原因分析
- 纯链接正文 → Gmail判定为钓鱼/垃圾
- 大量"论文""理论""突破"词汇 → 垃圾词触发
- 匿名邮箱（QQ/163）发学术机构邮箱 → 信誉分低
- 无DKIM/SPF签名的个人邮箱 → 高概率进垃圾箱

## 标准模板

```
主题: Question about [对方研究领域关键词] — structural approach

正文:

Hi [对方名字],

I read your work on [具体论文/研究]. The [某个具体点] reminded me of a structural pattern I've been exploring — coupling-induced decoherence steps that may generalize across domains.

I've written up the framework (four axioms, with mathematical proofs and experimental protocols). The Gitee repository is here:
https://gitee.com/samforce/structural-cognition

No pressure to read it. But if the discrete decoherence step prediction connects to your work, I'd be interested in your thoughts.

—
Lin Xiaohei (林小黑)
Guangzhou, China
```

## 关键规则

1. **主题行不放"论文""投稿""AI"** — 放对方研究领域的具体关键词
2. **正文不提"新理论""突破"** — 用"an approach I've been exploring"
3. **链接用Gitee（国内直访）不用rentry（被墙）**
4. **署名用真名+城市** — 增加可信度
5. **不超过150词** — 长邮件降低打开率
6. **不群发** — Gmail检测BCC群发
7. **先发一封测试到自己Gmail** — 确认不进垃圾箱再发真人
