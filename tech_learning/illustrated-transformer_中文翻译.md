# The Illustrated Transformer 中文翻译

> **原文：** [The Illustrated Transformer – Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
> **作者：** Jay Alammar
> **翻译日期：** 2026-06-05
> **翻译者：** Ku's Jarvis (MiniMax-M3)
> **目录：** `tech_learning/`

---

## 一句话总结

用可视化讲清楚 Transformer 的每个组件,**学 LLM 的必读第一篇** 🚀

---

## 简介

在上一篇文章里,我们讲了 **Attention** —— 一个在现代深度学习模型里无处不在的方法,它显著提升了神经机器翻译(Neural Machine Translation)的性能。本文要看的是 **Transformer** —— 一个用 Attention 来大幅提升训练速度的模型。

Transformer 在特定任务上击败了 Google 的神经机器翻译模型,但最大的好处来自它**天生适合并行化**。Google Cloud 实际上也推荐用 Transformer 作为他们 Cloud TPU 的参考模型。

Transformer 出自论文《[Attention is All You Need](https://arxiv.org/abs/1706.03762)》(arXiv:1706.03762)。TensorFlow 实现在 Tensor2Tensor 包里,Harvard NLP 组做了一个配套的 PyTorch 注释版指南。本文会做适度简化,把概念一个一个讲清楚。

> 📌 **2025 更新**:原文作者已经把这些内容扩展成了一本书 [LLM-book.com](https://llm-book.com),新增了 Multi-Query Attention、RoPE 等过去 7 年的演进内容。
>
> 📌 **2025 短课**:[free short course](https://bit.ly/4aRnn7Z) —— 用动画把本文内容更新到最新版。

本文已被以下顶尖高校课程收录:
- Stanford CS224N
- Harvard CS287
- MIT 6.S897
- Princeton COS597G
- CMU MLDL22W

---

## A High-Level Look(高层视角)

先把它当一个黑盒看:在机器翻译任务里,输入一个语言的句子,输出另一种语言。

> 🖼️ [图:黑盒图 + 打开后看到编码器、解码器、连接]

打开这个"擎天柱"(译注:Optimus Prime 双关),可以看到:

- **编码组件**:一堆编码器(论文里叠了 6 个,数字 6 没有魔法,可以实验)
- **解码组件**:同样数量的解码器堆叠

每个编码器结构完全一样(但不共享权重),分两个子层:

1. **Self-Attention 自注意力层** —— 帮编码器在编码某个词时"看"句子里的其他词
2. **前馈神经网络(FFNN)** —— 同样的网络,对每个位置独立应用

解码器也有这两个子层,但**中间多了一个 Attention 层**,帮解码器聚焦输入句子的相关部分(类似 seq2seq 里的 Attention 行为)。

> 🖼️ [图:编码器和解码器堆叠的全景图]

---

## Bringing The Tensors Into The Picture(把张量带进来)

NLP 任务第一步:把每个词用**词嵌入(embedding)**算法转成向量。每个词嵌入成 512 维的向量。

> 🖼️ [图:每个词变成 512 维小方块]

- 嵌入只发生在**最底层的编码器**
- 所有编码器抽象上都是:接收一个 512 维向量列表,输出一个 512 维向量列表
- 列表长度是超参数(基本就是训练集最长句子的长度)

> 🖼️ [图:嵌入向量从最底层开始向上流动]

**关键性质**:每个位置的词在编码器里走自己的路径。Self-Attention 层这些路径之间有依赖,但 FFNN 没有依赖,所以 FFNN 路径可以**并行执行**。

---

## Now We're Encoding!(开始编码)

编码器接收向量列表 → 过 Self-Attention → 过 FFNN → 向上层传输出。

> 🖼️ [图:每个位置的词 → self-attention → FFNN → 向上]

---

## Self-Attention at a High Level(Self-Attention 高层)

不要以为 Self-Attention 是常识概念——作者本人也是读《Attention is All You Need》才第一次见。

经典例子:

> *"The animal didn't cross the street because it was too tired"*

"it" 指的是 "animal" 还是 "street"?对人来说简单,对算法不简单。

当模型处理 "it" 时,Self-Attention 让它把 "it" 和 "animal" 关联起来。

> 🖼️ [图:在第 5 个编码器编码 "it" 时,部分 Attention 机制聚焦到 "The Animal",把它的部分表示"烤"进了 "it" 的编码里]

**类比 RNN**:RNN 维护隐藏状态把前文的"理解"融入当前词;Self-Attention 就是 Transformer 实现同样目标的机制。

> 💡 **动手实践**:Tensor2Tensor Notebook 里可以加载 Transformer 模型,用交互式可视化检查 Attention 行为。

---

## Self-Attention in Detail(Self-Attention 详解)

### 第一步:生成 Q、K、V 三个向量

从每个输入向量生成 3 个向量 —— **Query**、**Key**、**Value**。把 embedding 乘以 3 个训练好的矩阵 **W^Q**、**W^K**、**W^V** 得到。

> 🖼️ [图:x1 × W^Q = q1;q/k/v 三组向量]

注意:**q/k/v 维度是 64**,比 embedding(512)小。这不是必须,是架构选择,让多头 Attention 的计算量大致恒定。

> **Q/K/V 是什么?** 抽象概念。看完下面计算就懂它们各自的作用。

### 第二步:打分

算第一个词 "Thinking" 的 Self-Attention,要给输入句子的每个词打分。分数决定编码该词时,对其他词的"关注度"。

**打分 = query 向量和 key 向量的点积**

- 第 1 个分数 = q₁ · k₁
- 第 2 个分数 = q₁ · k₂
- ...

### 第三、第四步:归一化

分数除以 8(key 维度的平方根,√64 = 8,这样梯度更稳定),然后过 **softmax**。Softmax 把分数归一化到全正、和为 1。

Softmax 分数决定每个词在该位置的表达程度。

> 🖼️ [图:点积 → ÷8 → softmax 流程图]

### 第五步:加权

每个 value 向量乘以 softmax 分数。

> **直觉**:保留要关注的词的值,淹没不相关的(乘以 0.001 这种小数字)。

### 第六步:求和

把加权后的 value 向量求和。得到该位置的 Self-Attention 输出。

> 🖼️ [图:六步完整流程的可视化]

这就是 Self-Attention 计算。结果向量送进 FFNN。实际实现用**矩阵形式**加速,下面看。

---

## Matrix Calculation of Self-Attention(矩阵形式)

第一步:算 **Q**、**K**、**V** 矩阵。把所有 embedding 打包成矩阵 **X**,乘以训练好的 **W^Q**、**W^K**、**W^V**。

> 🖼️ [图:X 矩阵每一行 = 一个词;embedding 512 维(4 框),q/k/v 64 维(3 框)]

最后用一行公式压缩步骤 2~6:

> 🖼️ [图:Self-Attention 矩阵计算公式]

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$

这就是大名鼎鼎的 **Scaled Dot-Product Attention** 公式。

---

## The Beast With Many Heads(多头怪兽)

论文进一步引入了**多头 Attention(Multi-Head Attention)**,从两方面提升性能:

1. **扩展关注不同位置的能力**。单头时 z₁ 含其他编码的"一点",但可能自身词占主导。多头能更好处理"it 指代"问题
2. **多个"表示子空间"**。不再只有一组 Q/K/V 权重,而是 **8 组**(论文 8 头),每组随机初始化,训练后各自把输入投影到不同的子空间

> 🖼️ [图:多头下,每个头有独立的 W^Q/W^K/W^V]

同样 Self-Attention 计算 8 次 → 8 个不同的 **Z** 矩阵。

**挑战**:FFNN 不接受 8 个矩阵,要单个矩阵(每个词一个向量)。**怎么合并?** 把 8 个矩阵 **concat** 起来,乘以一个额外的权重矩阵 **W^O**。

> 🖼️ [图:8 头 Z → concat → × W^O → 单矩阵]

回到 "it" 例子看不同头在关注什么:

> 🖼️ [图:一个头聚焦 "the animal",另一个聚焦 "tired"——多头把不同相关词的表示都烤进 "it" 的编码里]

如果把所有头都画到一个图里,会变得难以解释:

> 🖼️ [图:所有 8 个头的注意力分布叠在一起]

---

## Representing The Order of The Sequence Using Positional Encoding(用位置编码表示序列顺序)

模型还缺一个东西:**如何表示输入序列中词的顺序**。

解决方案:给每个输入 embedding **加一个向量**。这些向量遵循特定模式,模型学得后能确定每个词的位置、或词与词之间的距离。

> 🖼️ [图:embedding + 位置编码向量]

如果 embedding 维度是 4,实际位置编码长这样:

> 🖼️ [图:4 维玩具示例]

20 个词、512 维的真实编码:

> 🖼️ [图:颜色编码,20 行 × 512 列;左半用 sine,右半用 cosine,拼接成位置编码]

📌 公式在论文 3.5 节。代码在 Tensor2Tensor 的 `get_timing_signal_1d()`。**好处**:能泛化到训练时没见过的更长序列。

> ⚠️ **2020 更新**:上面是 Tensor2Tensor 实现(sine/cosine 直接拼接);论文原版是**交织**两种信号(不一样)。[生成代码](https://github.com/jalammar/jalammar.github.io/blob/master/notebookes/transformer/transformer_positional_encoding_graph.ipynb)

---

## The Residuals(残差连接)

每个子层(self-attention、ffnn)都有一个**残差连接(residual connection)**包着它,然后跟一个 **layer-normalization**。

> 🖼️ [图:向量 + layer-norm 可视化]

解码器子层也一样。如果是 2 层堆叠的 Transformer:

> 🖼️ [图:2 层 encoders + 2 层 decoders 全景]

**作用**:残差连接让梯度可以无损地反向传播,层数很深(几十上百层)的 Transformer 才能稳定训练。

---

## The Decoder Side(解码器侧)

编码器侧基本讲完,解码器组件工作方式类似。看看它们怎么协作。

### 整体工作流

1. 编码器处理输入序列
2. 顶层编码器的输出 → 转成一组 attention 向量 **K** 和 **V**
3. 每个解码器在 "**编码器-解码器 Attention 层**" 里用这组 K、V,聚焦输入的相关部分

> 🖼️ [图:从编码器顶输出的 K、V → 进入每个解码器]

### 解码器的子层

解码器每个时间步输出**一个翻译后的词**。重复这个过程,直到碰到特殊符号「**EOS**」停止。

> 🖼️ [图:解码器逐词生成示意]

每个解码器子层有两个 Attention 输入:

- 来自**编码器的 K、V**(编码器-解码器 Attention 用)
- 来自**解码器自身前一步输出**(Masked Self-Attention 用)

### Masked Self-Attention(掩码自注意力)

**关键差异**:解码器 Self-Attention 只能看**当前位置之前**的位置(用 Mask 屏蔽未来位置)。

> 🖼️ [图:解码器 Self-Attention 自回归结构 —— 只能关注已生成的位置]

⚠️ **编码器 Self-Attention**:一次性看到整个输入序列。
⚠️ **解码器 Self-Attention**:只能看已生成的位置。这是**自回归(autoregressive)** 生成的关键——生成第 N 个词时,不能"偷看"还没生成的第 N+1、N+2 个词。

---

## The Final Linear and Softmax Layer(最终线性层和 Softmax)

解码器最终输出一个浮点数向量,怎么转成词?

> 🖼️ [图:解码器堆 → Linear 层 → Logits 向量 → Softmax → 概率分布 → 选词]

### 流程

1. **Linear 层**:把解码器输出向量投影成一个大向量 **logits**,长度 = **vocab size**(词表大小,比如 10000)
2. **Softmax 层**:把 logits 转成概率分布,全正、和为 1
3. **选词**:选概率最高的词(推理时)→ 输出这个词,作为下一步的输入

> 🖼️ [图:每个位置产生一个 logit 向量 → softmax → 概率]

### 训练 vs 推理细节

- **训练时**:解码器**并行**处理所有位置(即使"未来"位置也被计算),用 **Mask** 屏蔽掉注意力
- **推理时**:必须**逐词**生成,一个一个来
- **工程上**:训练好模型后,**beam search** 等技巧可提升输出质量

---

## The Training(训练)

训练一个 Transformer,核心是让它学会输出正确翻译。

### 流程

1. **数据准备**:成对标注语料(比如 WMT 数据集)
2. **前向传播**:把句子过一遍 Transformer,输出概率分布
3. **损失计算**:对比输出概率 vs 真实目标词 → **交叉熵损失(cross-entropy loss)**
4. **反向传播**:损失往回传,调整权重
5. **优化器更新**:**Adam** 等优化器沿梯度方向调权重
6. 重复 N 个 epoch

> 🖼️ [图:训练循环 —— 数据 → 前向 → 损失 → 反向 → 更新]

💡 **教学环境**:推荐 Harvard NLP 的「[The Annotated Transformer](http://nlp.seas.harvard.edu/2018/04/03/attention.html)」—— 论文 + PyTorch 实现逐行注释。

---

## 🎓 库哥导读:核心要点

### 必抓的 6 个核心概念

| # | 概念 | 一句话 |
|---|------|--------|
| 1 | 🧱 **Encoder-Decoder 架构** | 6 个编码器 + 6 个解码器堆叠 |
| 2 | 🎯 **Self-Attention** | Q/K/V 三个向量 + 点积 + Softmax + 加权求和 |
| 3 | 🐙 **Multi-Head Attention** | 8 个头并行,各自学不同子空间 |
| 4 | 📍 **Positional Encoding** | sin/cos 编码,弥补 Transformer 无序的缺陷 |
| 5 | 🛡️ **Masked Self-Attention** | 解码器侧用 Mask 防止偷看未来 |
| 6 | 🔄 **残差连接 + LayerNorm** | 每个子层标配,训练深网络关键 |

### 关键公式

```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

### 学习路径建议(接 LLM 学习计划)

1. ✅ **本文** —— Transformer 整体直觉
2. ➡️ 论文《Attention is All You Need》—— 原始细节
3. ➡️ Harvard NLP [The Annotated Transformer](http://nlp.seas.harvard.edu/2018/04/03/attention.html) —— 论文 + PyTorch 代码
4. ➡️ [LLM-book.com](https://llm-book.com) 第三章 —— 7 年演进(Multi-Query Attention、RoPE 等)
5. ➡️ 视频课程 —— MIT 6.S898 / Stanford CS224N

### 配套资源

- 中文翻译版本 1(CSDN):[blog.csdn.net/yujianmin1990/article/details/85221271](https://blog.csdn.net/yujianmin1990/article/details/85221271)
- 中文翻译版本 2(CSDN):[blog.csdn.net/qq_36667170/article/details/124359818](https://blog.csdn.net/qq_36667170/article/details/124359818)
- Annotated Transformer(PyTorch):[nlp.seas.harvard.edu/2018/04/03/attention.html](http://nlp.seas.harvard.edu/2018/04/03/attention.html)
- Tensor2Tensor 笔记本:colab 上有交互式可视化
- 2025 短课(含动画):[bit.ly/4aRnn7Z](https://bit.ly/4aRnn7Z)
- 论文:[arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762)

---

## 📝 翻译说明

- 保留原文章节标题的英文(方便对照原图)
- 配图说明部分用「🖼️」标注
- 专业术语首次出现给"中文(英文)"对照
- 数学公式保留原样
- 结尾追加「🎓 库哥导读」:核心要点 + 学习路径建议

---

*翻译日期:2026-06-05*
*翻译者:Ku's Jarvis (MiniMax-M3)*
