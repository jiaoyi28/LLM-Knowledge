"""
手动实现 Transformer 架构（基于 PyTorch）。

实现目标：
1. 不使用 `torch.nn.Transformer` 高阶封装；
2. 显式实现多头注意力、前馈网络、编码器层、解码器层；
3. 提供清晰的掩码逻辑（padding mask + causal mask）；
4. 注释尽量详细，便于学习与二次修改。
"""

import math
from typing import Optional, Tuple

import torch
import torch.nn as nn


class PositionalEncoding(nn.Module):
    """
    正弦/余弦位置编码（Sinusoidal Positional Encoding）。

    Transformer 本身没有循环结构（RNN）和卷积结构（CNN），
    需要额外注入“位置信息”让模型知道 token 的先后顺序。

    公式（论文 Attention Is All You Need）：
        PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
        PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    """

    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1) -> None:
        super().__init__()
        self.dropout = nn.Dropout(dropout)

        # pe 的形状: [max_len, d_model]
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)  # [max_len, 1]
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float) * (-math.log(10000.0) / d_model)
        )  # [d_model/2]

        # 偶数维使用 sin，奇数维使用 cos
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        # 注册为 buffer：随模型保存/加载，但不是可训练参数
        # 扩展为 [1, max_len, d_model]，方便与 batch 维广播
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: [batch_size, seq_len, d_model]
        Returns:
            [batch_size, seq_len, d_model]
        """
        seq_len = x.size(1)
        x = x + self.pe[:, :seq_len]
        return self.dropout(x)


class MultiHeadAttention(nn.Module):
    """
    多头注意力（Multi-Head Attention）。

    关键流程：
    1) 线性投影得到 Q/K/V；
    2) 拆分为多个 head；
    3) 每个 head 执行缩放点积注意力；
    4) 拼接 head 结果，再做输出投影。
    """

    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1) -> None:
        super().__init__()
        if d_model % num_heads != 0:
            raise ValueError("d_model 必须能被 num_heads 整除。")

        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads

        # 分别对 q/k/v 做线性映射
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)

        # 多头拼接后再做一次线性变换
        self.w_o = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def _split_heads(self, x: torch.Tensor) -> torch.Tensor:
        """
        将 [B, L, D] 拆为 [B, H, L, Dh]
        B: batch, L: seq_len, D: d_model, H: num_heads, Dh: head_dim
        """
        batch_size, seq_len, _ = x.size()
        x = x.view(batch_size, seq_len, self.num_heads, self.head_dim)
        return x.transpose(1, 2)

    def _merge_heads(self, x: torch.Tensor) -> torch.Tensor:
        """
        将 [B, H, L, Dh] 合并回 [B, L, D]
        """
        batch_size, _, seq_len, _ = x.size()
        x = x.transpose(1, 2).contiguous()
        return x.view(batch_size, seq_len, self.d_model)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            query/key/value: [B, L, D]
            mask:
                允许以下形状之一，并自动广播到 [B, H, Lq, Lk]:
                - [B, 1, 1, Lk]      (padding mask)
                - [B, 1, Lq, Lk]     (padding + causal 组合 mask)
                - [B, Lq, Lk]        (会自动扩展到 [B, 1, Lq, Lk])
            mask 中 True 表示“可见”，False 表示“需要屏蔽”。
        Returns:
            output: [B, Lq, D]
            attn_weights: [B, H, Lq, Lk]
        """
        q = self._split_heads(self.w_q(query))  # [B, H, Lq, Dh]
        k = self._split_heads(self.w_k(key))    # [B, H, Lk, Dh]
        v = self._split_heads(self.w_v(value))  # [B, H, Lk, Dh]

        # 缩放点积注意力分数: [B, H, Lq, Lk]
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        # 统一 mask 形状，最终希望可广播到 [B, H, Lq, Lk]
        if mask is not None:
            if mask.dim() == 3:
                mask = mask.unsqueeze(1)  # [B, 1, Lq, Lk]
            # 用一个非常小的值填充被屏蔽位置，softmax 后近似 0
            scores = scores.masked_fill(~mask, torch.finfo(scores.dtype).min)

        attn_weights = torch.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        # 注意力加权求和: [B, H, Lq, Dh]
        context = torch.matmul(attn_weights, v)
        context = self._merge_heads(context)  # [B, Lq, D]

        output = self.w_o(context)
        return output, attn_weights


class PositionwiseFeedForward(nn.Module):
    """
    前馈网络（FFN）：
        Linear(d_model -> d_ff) + 激活 + Dropout + Linear(d_ff -> d_model)

    注意：这是对序列中每个位置独立地做同一个 MLP，因此称为 position-wise。
    """

    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class EncoderLayer(nn.Module):
    """
    编码器层：
    1) 自注意力（Self-Attention）
    2) 前馈网络（FFN）
    每个子层都包含残差连接 + LayerNorm（Post-LN 风格）。
    """

    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1) -> None:
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.ffn = PositionwiseFeedForward(d_model, d_ff, dropout)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        src_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        # 子层 1: 自注意力 + 残差 + 归一化
        attn_out, _ = self.self_attn(x, x, x, src_mask)
        x = self.norm1(x + self.dropout(attn_out))

        # 子层 2: 前馈 + 残差 + 归一化
        ffn_out = self.ffn(x)
        x = self.norm2(x + self.dropout(ffn_out))
        return x


class DecoderLayer(nn.Module):
    """
    解码器层：
    1) Masked Self-Attention（防止看到未来 token）
    2) Cross-Attention（Q 来自 decoder，K/V 来自 encoder）
    3) 前馈网络（FFN）
    每个子层都包含残差连接 + LayerNorm。
    """

    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1) -> None:
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.cross_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.ffn = PositionwiseFeedForward(d_model, d_ff, dropout)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        memory: torch.Tensor,
        tgt_mask: Optional[torch.Tensor] = None,
        memory_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        # 子层 1: masked self-attn
        self_attn_out, _ = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(self_attn_out))

        # 子层 2: cross-attn (query=x, key/value=memory)
        cross_attn_out, _ = self.cross_attn(x, memory, memory, memory_mask)
        x = self.norm2(x + self.dropout(cross_attn_out))

        # 子层 3: FFN
        ffn_out = self.ffn(x)
        x = self.norm3(x + self.dropout(ffn_out))
        return x


class Encoder(nn.Module):
    """
    Transformer Encoder（多层堆叠）。
    """

    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        num_layers: int,
        num_heads: int,
        d_ff: int,
        dropout: float = 0.1,
        max_len: int = 5000,
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len=max_len, dropout=dropout)
        self.layers = nn.ModuleList(
            [EncoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)]
        )
        self.dropout = nn.Dropout(dropout)
        self.d_model = d_model

    def forward(
        self,
        src_tokens: torch.Tensor,
        src_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        # embedding 后乘 sqrt(d_model) 是论文中的常见做法，帮助数值尺度稳定
        x = self.embedding(src_tokens) * math.sqrt(self.d_model)
        x = self.pos_encoding(x)
        x = self.dropout(x)

        for layer in self.layers:
            x = layer(x, src_mask)
        return x


class Decoder(nn.Module):
    """
    Transformer Decoder（多层堆叠）。
    """

    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        num_layers: int,
        num_heads: int,
        d_ff: int,
        dropout: float = 0.1,
        max_len: int = 5000,
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len=max_len, dropout=dropout)
        self.layers = nn.ModuleList(
            [DecoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)]
        )
        self.dropout = nn.Dropout(dropout)
        self.d_model = d_model

    def forward(
        self,
        tgt_tokens: torch.Tensor,
        memory: torch.Tensor,
        tgt_mask: Optional[torch.Tensor] = None,
        memory_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        x = self.embedding(tgt_tokens) * math.sqrt(self.d_model)
        x = self.pos_encoding(x)
        x = self.dropout(x)

        for layer in self.layers:
            x = layer(x, memory, tgt_mask, memory_mask)
        return x


class Transformer(nn.Module):
    """
    完整 Transformer（Encoder-Decoder）。

    输出层会把 decoder hidden states 映射到目标词表维度，得到 logits。
    """

    def __init__(
        self,
        src_vocab_size: int,
        tgt_vocab_size: int,
        d_model: int = 512,
        num_layers: int = 6,
        num_heads: int = 8,
        d_ff: int = 2048,
        dropout: float = 0.1,
        max_len: int = 5000,
        pad_idx: int = 0,
    ) -> None:
        super().__init__()
        self.encoder = Encoder(
            vocab_size=src_vocab_size,
            d_model=d_model,
            num_layers=num_layers,
            num_heads=num_heads,
            d_ff=d_ff,
            dropout=dropout,
            max_len=max_len,
        )
        self.decoder = Decoder(
            vocab_size=tgt_vocab_size,
            d_model=d_model,
            num_layers=num_layers,
            num_heads=num_heads,
            d_ff=d_ff,
            dropout=dropout,
            max_len=max_len,
        )
        self.output_proj = nn.Linear(d_model, tgt_vocab_size)
        self.pad_idx = pad_idx

    @staticmethod
    def make_padding_mask(tokens: torch.Tensor, pad_idx: int) -> torch.Tensor:
        """
        创建 padding mask。

        Args:
            tokens: [B, L]
        Returns:
            mask: [B, 1, 1, L]，True 表示有效 token，False 表示 padding。
        """
        return (tokens != pad_idx).unsqueeze(1).unsqueeze(2)

    @staticmethod
    def make_causal_mask(seq_len: int, device: torch.device) -> torch.Tensor:
        """
        创建因果 mask（下三角）。

        Returns:
            [1, 1, L, L]，位置 (i, j) 仅当 j <= i 时为 True。
        """
        mask = torch.tril(torch.ones(seq_len, seq_len, dtype=torch.bool, device=device))
        return mask.unsqueeze(0).unsqueeze(0)

    def make_tgt_mask(self, tgt_tokens: torch.Tensor) -> torch.Tensor:
        """
        组合目标端 mask = padding mask AND causal mask。

        结果形状 [B, 1, Lt, Lt]，可直接用于 decoder 的 self-attention。
        """
        batch_size, tgt_len = tgt_tokens.size()
        _ = batch_size  # 明确告诉读者该维度已在广播中体现

        padding_mask = self.make_padding_mask(tgt_tokens, self.pad_idx)      # [B,1,1,Lt]
        causal_mask = self.make_causal_mask(tgt_len, tgt_tokens.device)      # [1,1,Lt,Lt]
        return padding_mask & causal_mask

    def forward(self, src_tokens: torch.Tensor, tgt_tokens: torch.Tensor) -> torch.Tensor:
        """
        Args:
            src_tokens: [B, Ls]
            tgt_tokens: [B, Lt]
        Returns:
            logits: [B, Lt, tgt_vocab_size]
        """
        # 编码端 mask：用于 encoder self-attn（屏蔽源序列中的 padding）
        src_mask = self.make_padding_mask(src_tokens, self.pad_idx)  # [B,1,1,Ls]

        # 解码端 self-attn mask：同时包含 padding + causal
        tgt_mask = self.make_tgt_mask(tgt_tokens)                    # [B,1,Lt,Lt]

        # cross-attn mask：query 来自 tgt，key/value 来自 src
        # 只需屏蔽 src 里的 padding，因此复用 src_mask 即可（会自动广播到 Lt 维）
        memory_mask = src_mask                                       # [B,1,1,Ls]

        memory = self.encoder(src_tokens, src_mask=src_mask)  # [B, Ls, D]
        dec_out = self.decoder(
            tgt_tokens,
            memory=memory,
            tgt_mask=tgt_mask,
            memory_mask=memory_mask,
        )  # [B, Lt, D]

        logits = self.output_proj(dec_out)  # [B, Lt, Vt]
        return logits


if __name__ == "__main__":
    # ----------------------------
    # 简单的可运行示例（仅用于结构检查）
    # ----------------------------
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = Transformer(
        src_vocab_size=10000,
        tgt_vocab_size=12000,
        d_model=256,
        num_layers=4,
        num_heads=8,
        d_ff=1024,
        dropout=0.1,
        max_len=256,
        pad_idx=0,
    ).to(device)

    # 构造一批假数据：[batch, seq_len]
    src = torch.randint(1, 9999, (2, 16), device=device)
    tgt = torch.randint(1, 11999, (2, 12), device=device)

    # 人为插入 padding，测试 mask 是否兼容
    src[:, -2:] = 0
    tgt[:, -1:] = 0

    logits = model(src, tgt)
    print("logits shape:", logits.shape)  # 期望: [2, 12, 12000]
