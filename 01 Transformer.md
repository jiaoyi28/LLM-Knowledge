Transformer架构起源于 Attention is all you need这篇论文，并引发了在AI领域的爆发式进展
![[file-20260304211121112.png]]

Transformer大致分为几个结构：Embedding、位置编码、多头注意力、Mask

# 1 Embedding
文字并不能直接被模型消费，需要转化成embedding，以下是具体步骤
1. tokenization：将文字切分成最小单元，比如
	1. `I like Transformers`-> `['i', 'like', 'transform', '##ers']`
	2. `我喜欢Transformer架构`-> `['我', '喜欢', 'transform', '##ers', '架构']`
2. token -> token ID：只用指定的词表（vocab）将每个token查表映射成`int`
3. token ID -> embedding：在模型中有一个可学习的Embedding Matrix, $$E \in R^{V \times d_{model}}$$，其中V是词表的大小，$d_{model}$是embedding的维度，通常为512、1024、4096等。每一个`int`类型的token ID对应 $E$ 中的一行向量 $e^{1 \times d_{model}}$
经过前面三步的转化，一个句子就会转化为一个 $seq\_len \times d_{model}$大小的embedding matrix，其中 $seq\_len$ 是token数或者叫序列长度。
假设 $d_{model} = 512$， `我喜欢Transformer架构`-> `['我', '喜欢', 'transform', '##ers', '架构']`共5个token，最终会得到一个 $5 \times 512$的embedding matrix，被称为 Input Embedding

# 2 位置编码
![[file-20260304211235503.png]]

上一步得到的 Input Embedding不会直接进行计算，需要增加位置编码，使得最后的输入满足：$$input = input\_embedding_{seq\_len \times d^{model}} + positional\_embedding_{seq\_len \times d^{model}}$$
那么，我们为什么需要position encoding呢？在transformer的self-attention模块中，序列的输入输出如下:
![[file-20260304214119213.png]]
在self-attention模型中，输入是一整排的tokens，对于人来说，我们很容易知道tokens的位置信息，比如：  
1. 绝对位置信息。a1是第一个token，a2是第二个token......  
2. 相对位置信息。a2在a1的后面一位，a4在a2的后面两位......  
3. 不同位置间的距离。a1和a3差两个位置，a1和a4差三个位置....  
**但是这些对于self-attention来说，是无法分辩的信息，因为self-attention的运算是无向的。因为，我们要想办法，把tokens的位置信息，喂给模型。**

## 位置编码的演化
位置编码的方法有很多种，比如按照token顺序依次标记1，2，3...；或者在 $[0, 1]$ 区间内等分0，0.33，0.69，1；一直到使用 $sin, cos$

具体的推导和说明可以参考[这篇文章](https://zhuanlan.zhihu.com/p/454482273)

最终transformer论文中采用的位置编码如下：$$PE_{t}^{(i)} = \begin{cases} sin(\omega_{k}t), &if \ i == 2k\\cos(\omega_{k}t),&if \ i == 2k+1 \end{cases}$$
其中，$t$ 是token在序列中的位置，1，2，3...
$PE_{t} \in R^{d_{model}}$ 是位置编码向量，$PE_{t}^{(i)}$ 是位置编码的第 $i$ 个元素
$\omega_k = {1 \over 10000^{2k/d_{model}}}, \ where \ i=0,1,2...$
仍旧以前面的`我喜欢Transformer架构`为例，得到的位置编码为 $PE = \begin{Bmatrix} PE_1 \\ PE_2 \\ PE_3 \\ PE_4 \\ PE_5 \\\end{Bmatrix} \in R ^{5 \times d_{model}}$

# Attention
![[file-20260304220932322.png]]

## self-attention计算
上一步计算得到的 $$input = input\_embedding_{seq\_len \times d^{model}} + positional\_embedding_{seq\_len \times d^{model}}$$会首先分别经过 $W^{Q} \in R^{d^{model} \times k\_dim}$, $W^{K} \in R^{d^{model} \times k\_dim}$, $W^{V} \in R^{d^{model} \times v\_dim}$做矩阵乘法得到$Q, K, V$。在训练阶段，$W^{Q}, W^{K}, W^{V}$是可以被学习的
$W^{Q}, W^{K}$都使用 $k\_dim$，但是 $W^{V}$ 的 $v\_dim$不一定等于$k\_dim$。在transformer中采用的是 $$k\_dim = v\_dim = d_{model} / num\_heads$$
![[file-20260304221149252.png]]
接着是计算attention score，$$Attention(Q, K, V) = softmax({QK^T \over \sqrt{d_k}}V) \in R^{seq\_len \times k\_dim}$$，其中 $d_k$ 就是 k_dim
![[file-20260304222924488.png]]
**（勘误：紫色方框中的下标应该是  $\alpha_{11}, \alpha_{12}, \alpha_{13}, \alpha_{14}$)**

**这里的 $1 \over \sqrt{d_k}$ 是scaling因子，之所以进行scaling，是为了使得在softmax的过程中，梯度下降得更加稳定，避免因为梯度过小而造成模型参数更新的停滞**。数学原理大致上是未经过scaling时，$QK^T$ 中的元素互相之间相差过大或者过小时，都会导致softmax函数的偏导趋近于0，导致梯度趋近于0。而经过scaling，元素之间就不会相差过多或者过少。主要是由于softmax函数的性质导致的（每行向量的元素和为1）
$$softmax(\alpha_{ij}) = {e^{\alpha_{ij}} \over \sum_{j=1}^{d_k} e^{\alpha_{ij}}}$$
## masked attention
上面介绍的是未经mask的attention score，但是在decoder中会使用到 masked attention，即将序列的一部分进行遮盖，让每个token只能看到它前面的序列而看不到后面的（对应的attention $\alpha_{ij}$ 趋近于0）。这样的操作可以理解为模型为了防止decoder在解码encoder层输出时“作弊”，提前看到了剩下的答案，因此需要强迫模型根据输入序列左边的结果进行attention。

具体实现就是通过 mask矩阵对 $Qk^T$ 的结果进行操作，$$Mask \in R^{seq\_len \times seq\_len} $$![[Drawing 2026-03-04 22.51.48.excalidraw.png]]
在MASK矩阵标1的地方，也就是需要遮蔽的地方，我们把原来的值替换为一个很小的值（比如-1e09），而在MASK矩阵标0的地方，我们保留原始的值。这样，在进softmax的时候，那些被替换的值由于太小，就可以自动忽略不计（值趋近于0），从而起到遮蔽的效果。

## multihead-attention
![[file-20260304230227294.png]]
不同的head，对应不同的模式识别，也会训练出不同的 $W^Q, W^K, W^V$
此外还会新增一个 $W^O$ 矩阵。多个head计算得到的多个 $Z_i$ 矩阵，$$Z_i \in R^{seq\_len \times k\_dim} , 即 \ Z_i \in R^{seq\_len \times  (d_{model} / num\_heads)}$$会首先按行进行拼接（concatenate），得到 $Z^*$， $$Z^* \in R^{seq\_len \times d\_model}$$，然后和 $W^O \in R^{d\_model \times k\_dim}$ 矩阵做乘法得到最终的multihead attention score矩阵 $Z$
 
 
 [原论文]([https://arxiv.org/abs/1706.03762]())
 