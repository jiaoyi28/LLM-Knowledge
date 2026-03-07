
# Transformer 代码实现讲解（含训练/推理 I/O 示例）

这篇文档结合 `code/transformer/transformer.py`、`code/transformer/inference_demo.py`、`code/transformer/inference_batch_beam.py`，用“先整体、再细节”的方式讲清楚 Transformer 是怎么在代码里跑起来的，并补充训练和推理阶段的真实输入输出格式。

---

## 1. 先看全局：目录里这三份代码分别做什么

- `transformer.py`：手写版 Encoder-Decoder Transformer（核心模型）
- `inference_demo.py`：单样本自回归贪心推理（逐步打印 `tgt_tokens`）
- `inference_batch_beam.py`：批量推理入口，支持 greedy 和 beam

主模型不依赖 `torch.nn.Transformer` 高阶封装，而是显式实现：

- `PositionalEncoding`
- `MultiHeadAttention`
- `PositionwiseFeedForward`
- `EncoderLayer` / `DecoderLayer`
- `Encoder` / `Decoder`
- `Transformer`（含 mask 构造和输出投影）

---

## 2. 统一记号与张量形状（最关键）

约定：

- `B`：batch size
- `Ls`：源序列长度（source length）
- `Lt`：目标序列长度（target length）
- `D`：隐藏维度（`d_model`）
- `H`：头数（`num_heads`）
- `Dh`：每头维度（`D / H`）
- `Vt`：目标词表大小

常见张量：

- `src_tokens`：`[B, Ls]`
- `tgt_tokens`：`[B, Lt]`
- `memory`（encoder 输出）：`[B, Ls, D]`
- `dec_out`：`[B, Lt, D]`
- `logits`：`[B, Lt, Vt]`

注意力里的关键变形：

- 先把 `[B, L, D]` 拆成 `[B, H, L, Dh]`
- 做完注意力再合并回 `[B, L, D]`

---

## 3. 位置编码：`PositionalEncoding`

为什么需要：Transformer 没有 RNN 的时间顺序，需要显式注入位置信息。

实现要点：

- 构造 `pe: [max_len, d_model]`
- 偶数维 `sin`、奇数维 `cos`
- `register_buffer("pe", pe.unsqueeze(0))` 保存为 `[1, max_len, d_model]`
- `forward` 时裁切到当前长度并与输入相加

输入输出：

- 输入 `x`：`[B, L, D]`
- 输出：`[B, L, D]`

---

## 4. 多头注意力：`MultiHeadAttention`（核心）

执行流程：

1. 线性映射得到 `Q/K/V`
2. `split_heads`：`[B, L, D] -> [B, H, L, Dh]`
3. 计算 `scores = Q @ K^T / sqrt(Dh)`
4. 应用 mask（屏蔽位填最小值）
5. `softmax(scores)` 得到权重
6. 权重与 `V` 相乘得到上下文
7. 合并多头并输出线性层

mask 约定（非常重要）：

- `True` = 可见
- `False` = 屏蔽

可接受 mask 形状（自动广播）：

- `[B, 1, 1, Lk]`（padding）
- `[B, 1, Lq, Lk]`（padding + causal 组合）
- `[B, Lq, Lk]`（自动扩到 `[B, 1, Lq, Lk]`）

返回：

- `output`：`[B, Lq, D]`
- `attn_weights`：`[B, H, Lq, Lk]`

---

## 5. 前馈网络：`PositionwiseFeedForward`

结构：

`Linear(D -> d_ff) -> ReLU -> Dropout -> Linear(d_ff -> D)`

特点：对序列中每个位置独立应用同一套 MLP（参数共享）。

---

## 6. 编码器层 / 解码器层

### 6.1 `EncoderLayer`

- 子层 1：self-attention
- 子层 2：FFN
- 每个子层后：残差连接 + LayerNorm（Post-LN）

### 6.2 `DecoderLayer`

- 子层 1：masked self-attention（禁止看未来）
- 子层 2：cross-attention（Q 来自 decoder，K/V 来自 encoder）
- 子层 3：FFN
- 同样是残差 + LayerNorm

---

## 7. `Encoder` / `Decoder` 多层堆叠

`Encoder` 流程：

1. embedding
2. 乘 `sqrt(d_model)`
3. 位置编码 + dropout
4. 通过多层 `EncoderLayer`

`Decoder` 流程类似，但每层会使用：

- `tgt_mask`（用于 self-attention）
- `memory_mask`（用于 cross-attention）

---

## 8. 顶层 `Transformer`：关键是三种 mask

`forward(src_tokens, tgt_tokens)` 中：

1. `src_mask = make_padding_mask(src_tokens)`：`[B,1,1,Ls]`
2. `tgt_mask = make_tgt_mask(tgt_tokens)`：`[B,1,Lt,Lt]`
3. `memory_mask = src_mask`（给 cross-attention 用）

完整前向：

1. `memory = encoder(src_tokens, src_mask)`
2. `dec_out = decoder(tgt_tokens, memory, tgt_mask, memory_mask)`
3. `logits = output_proj(dec_out)`，得到 `[B, Lt, Vt]`

---

## 9. 训练阶段真实 I/O（Teacher Forcing）

训练时不会把完整目标句原封不动喂给 decoder，而是做“右移一位”：

- `tgt_in`：`<bos> y1 y2 ... y_{n-1}`
- `tgt_out`：`y1 y2 ... y_n <eos>`

模型调用：

- `logits = model(src_tokens, tgt_in)`，形状 `[B, Lt, Vt]`
- 与 `tgt_out` 对齐后做交叉熵损失

最小训练 step（示例）：

```python
import torch
import torch.nn.functional as F
from transformer import Transformer

pad_id = 0
bos_id = 1
eos_id = 2

model = Transformer(
    src_vocab_size=12000,
    tgt_vocab_size=12000,
    d_model=256,
    num_layers=4,
    num_heads=8,
    d_ff=1024,
    dropout=0.1,
    max_len=256,
    pad_idx=pad_id,
)

# 例子：B=2，源长度 Ls=6，目标(含 <bos>/<eos>)长度为 7
src_tokens = torch.tensor([
    [11, 53, 98, 77,  2, 0],
    [24, 35, 66,  2,  0, 0],
], dtype=torch.long)

tgt_full = torch.tensor([
    [bos_id,  7, 18, 23, 41, eos_id, 0],
    [bos_id,  9, 15, eos_id, 0,      0, 0],
], dtype=torch.long)

tgt_in = tgt_full[:, :-1]   # [B, 6]
tgt_out = tgt_full[:, 1:]   # [B, 6]

logits = model(src_tokens, tgt_in)  # [B, 6, 12000]
loss = F.cross_entropy(
    logits.reshape(-1, logits.size(-1)),
    tgt_out.reshape(-1),
    ignore_index=pad_id,
)
loss.backward()
```

这个训练示例里的模型输入输出可总结为：

- 输入：`src_tokens=[B, Ls]`、`tgt_in=[B, Lt]`
- 输出：`logits=[B, Lt, Vt]`
- 监督标签：`tgt_out=[B, Lt]`

---

## 10. 推理阶段真实 I/O（自回归）

推理时流程是：

1. 编码 `src_tokens`（固定不变）
2. `tgt_tokens` 从 `<bos_id>` 开始
3. 每轮调用 `model(src_tokens, tgt_tokens)`
4. 取最后位置 `logits[:, -1, :]` 选下一个 token
5. 追加到 `tgt_tokens`，直到 `<eos>` 或到达上限

这里的 `logits` 要重点理解：

- `model(src_tokens, tgt_tokens)` 输出形状是 `[B, Lt, Vt]`
- 其中 `B` 是 batch，`Lt` 是当前已生成序列长度，`Vt` 是目标词表大小
- `logits[b, t, :]` 表示：第 `b` 个样本在第 `t` 个位置上，对词表中每个 token 的“未归一化打分”
- “未归一化”表示它不是概率，可能为任意实数（正负都可以），值越大代表该 token 越可能

为什么只取 `logits[:, -1, :]`：

- 当前轮我们只需要“下一个 token”
- 已有前缀长度是 `Lt`，那么“下一个 token”的预测对应最后一个时间步 `t=Lt-1`
- 所以用 `last_logits = logits[:, -1, :]`，其形状为 `[B, Vt]`

`last_logits` 到下一个 token 的常见选择方式：

1. Greedy（本仓库 `inference_demo.py` 默认方式）  
   - `next_id = argmax(last_logits)`  
   - 含义：直接选分数最高的 token，稳定但可能缺少多样性
2. Sampling（随机采样）  
   - 先 `probs = softmax(last_logits / temperature)`  
   - 再按概率采样 `next_id ~ Categorical(probs)`  
   - 含义：保留随机性，可通过 `temperature` 控制发散程度
3. Beam Search（`inference_batch_beam.py`）  
   - 每步保留 top-k 候选并累计序列分数  
   - 最终按长度惩罚后的总分选最佳序列

一个数值化小例子（单样本）：

- 假设当前 `last_logits`（只看 4 个候选 token）是：`[2.3, 1.2, 3.8, -0.4]`
- softmax 后大致是：`[0.16, 0.05, 0.77, 0.02]`
- greedy 会选索引 `2`（概率最高）
- sampling 则大概率选 `2`，但也可能选 `0/1/3`

得到 `next_id` 后，统一执行：

- `tgt_tokens = cat([tgt_tokens, next_id], dim=1)`
- 继续下一轮 forward，直到生成 `<eos>` 或达到 `max_new_tokens`

`inference_demo.py` 中的 `greedy_decode`，以及 `inference_batch_beam.py` 中的 `greedy_decode_batch` / `beam_search_single`，都在实现上述逻辑。

---

## 11. 具体推理示例（单样本 greedy）

`inference_demo.py` 的 toy 词表是：

- `<pad>=0, <bos>=1, <eos>=2, <unk>=3`
- `"我"=4, "爱"=5, "北"=6, "京"=7, "天"=8, "安"=9, "门"=10`

如果用户输入文本是 `"我爱北京"`，希望模型续写 `"天安门"`，那么：

- `src_ids = [4, 5, 6, 7]`
- `src_tokens` 形状是 `[1, 4]`

一个理想的自回归生成过程（示意）：

- Step 0 初始token：`[1]`（只有 `<bos>`）
- Step 1 生成 `"天"`：`[1, 8]`
- Step 2 生成 `"安"`：`[1, 8, 9]`
- Step 3 生成 `"门"`：`[1, 8, 9, 10]`
- Step 4 生成 `<eos>`：`[1, 8, 9, 10, 2]`（停止）

最终解码结果（去掉特殊符号）为：`"天安门"`

每一步模型输出的最后一位概率来自：

- `logits`：`[1, 当前Lt, V]`
- `logits[:, -1, :]`：`[1, V]`

---

## 12. 具体推理示例（批量 greedy / beam）

`inference_batch_beam.py` 支持批量输入，例如：

- 文本 1：`"我爱北京"` -> `[4,5,6,7]`
- 文本 2：`"我爱北"` -> `[4,5,6]`

会先 padding 成 `src_tokens=[B, Ls]`，例如 `B=2, Ls=4`：

- 样本 1：`[4,5,6,7]`
- 样本 2：`[4,5,6,0]`

两种模式：

- greedy：一次前向同时解码整批样本（真正 batch）
- beam：批量入口 + 样本级束搜索（每条样本单独跑 beam）

beam 的候选打分要点：

- 累加每步 `log_prob`
- 用长度惩罚做排序：`score / length_penalty`

---

## 13. 训练与推理的差异总结（面试高频）

- 训练：并行算整段 `tgt_in`，用 `tgt_out` 做监督
- 推理：串行逐 token 生成，下一个 token 依赖之前生成结果
- 训练也有 causal mask，但目标序列是“已知真值前缀”
- 推理时前缀来自模型自己，误差会累计（exposure bias）

---

## 14. 建议的源码阅读顺序

1. `Transformer.forward`（先看总流程）
2. `make_padding_mask` / `make_causal_mask` / `make_tgt_mask`（吃透 mask）
3. `MultiHeadAttention`（核心）
4. `EncoderLayer`、`DecoderLayer`
5. `Encoder`、`Decoder`
6. `inference_demo.py`（理解自回归）
7. `inference_batch_beam.py`（理解批量与 beam）

---

## 15. 初学者自检清单

- `d_model % num_heads == 0` 是否成立
- mask 语义是否统一（本代码中 `True=可见`）
- `tgt_in/tgt_out` 是否正确右移对齐
- loss 是否 `ignore_index=pad_id`
- 推理时 `tgt_tokens` 是否逐步增长
- 输出 `logits` 最后一维是否等于目标词表

掌握这些点后，可以继续扩展：

- 把 `ReLU` 替换成 `GELU`
- 改为 Pre-LN 架构
- 给推理加 KV Cache
- 接入真实 tokenizer 与数据集

