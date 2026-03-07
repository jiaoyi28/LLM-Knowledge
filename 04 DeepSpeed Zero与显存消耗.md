DeepSpeed是由微软开发的分布式训练框架，而Zero则是其中的核心，被用来解决大模型训练中的显存开销问题。**ZeRO的思想就是用通讯换显存。**
---

## 大模型的显存消耗
### 存储分类
![[file-20260306195424415.png]]

存储主要分为两大块：Model States和Residual States  
**Model States**指和模型本身息息相关的，必须存储的内容，具体包括：

- **optimizer states**：[Adam优化](https://zhida.zhihu.com/search?content_id=225657093&content_type=Article&match_order=1&q=Adam%E4%BC%98%E5%8C%96&zhida_source=entity)算法中的momentum和variance
- **gradients**：模型梯度
- **parameters**：模型参数W

**Residual States**指并非模型必须的，但在训练过程中会额外产生的内容，具体包括：

- **activation**：激活值。在backward过程中使用链式法则计算梯度时会用到。有了它算梯度会更快，但它不是必须存储的，因为可以通过重新做Forward来算它。同时一些正向计算中的临时结果也是激活值
- **temporary buffers:** 临时存储。例如把梯度发送到某块GPU上做加总聚合时产生的存储。
- **unusable fragment memory**：碎片化的存储空间。虽然总存储空间是够的，但是如果取不到连续的存储空间，相关的请求也会被fail掉。对这类空间浪费可以通过内存整理来解决。

### 精度混合训练
知道了存储分类，进一步，我们想知道，假设模型的参数W大小是 $\Phi$，那么每一类存储具体占了多大的空间呢？  
在分析这个问题前，我们需要来了解**精度混合训练**。  
对于模型，我们肯定希望其参数越精准越好，也即我们用**fp32（单精度浮点数，存储占4byte）**来表示参数W。但是在forward和backward的过程中，fp32的计算开销也是庞大的。那么能否在计算的过程中，引入**fp16或bf16（半精度浮点数，存储占2byte）**，来减轻计算压力呢？于是，[混合精度训练](https://zhida.zhihu.com/search?content_id=225657093&content_type=Article&match_order=1&q=%E6%B7%B7%E5%90%88%E7%B2%BE%E5%BA%A6%E8%AE%AD%E7%BB%83&zhida_source=entity)就产生了，它的步骤如下图：

![[file-20260306195844783.png]]
- 存储一份fp32的parameter，momentum和variance（统称model states）
- 在forward开始之前，额外开辟一块存储空间，将fp32 parameter减半到fp16 parameter。
- 正常做forward和backward，在此之间产生的activation和gradients，都用fp16进行存储。
- 用fp16 gradients去更新fp32下的model states。
- 当模型收敛后，fp32的parameter就是最终的参数输出。

通过这种方式，混合精度训练在计算开销和模型精度上做了权衡。如果不了解fp32，fp16和bf16的细节也没关系，不影响下文的阅读。只要记住它们所占的存储空间和精度表达上的差异即可。

