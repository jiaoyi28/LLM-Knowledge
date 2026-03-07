"""
Transformer 真实推理示例（自回归解码）。

用法示例：
    python inference_demo.py
    python inference_demo.py --text 我爱北京 --max-new-tokens 6
    python inference_demo.py --ckpt transformer_ckpt.pt

说明：
1) 该脚本演示“推理流程”而非效果保证；
2) 若不加载训练好的 checkpoint，输出基本是随机的；
3) 重点是展示 src_tokens / tgt_tokens 在推理阶段如何变化；
4) 在训练充分的情况下，可把“我爱北京”续写为“天安门”。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import torch

from transformer import Transformer


@dataclass
class ToyTokenizer:
    token_to_id: Dict[str, int]

    @property
    def id_to_token(self) -> Dict[int, str]:
        return {v: k for k, v in self.token_to_id.items()}

    @property
    def pad_id(self) -> int:
        return self.token_to_id["<pad>"]

    @property
    def bos_id(self) -> int:
        return self.token_to_id["<bos>"]

    @property
    def eos_id(self) -> int:
        return self.token_to_id["<eos>"]

    @property
    def unk_id(self) -> int:
        return self.token_to_id["<unk>"]

    def encode(self, text: str) -> List[int]:
        # 用“单字级”编码，便于直观看中文句子推理过程
        return [self.token_to_id.get(ch, self.unk_id) for ch in list(text)]

    def decode(self, ids: List[int]) -> str:
        special = {"<pad>", "<bos>", "<eos>"}
        tokens = [
            self.id_to_token.get(i, "<unk>")
            for i in ids
            if self.id_to_token.get(i, "<unk>") not in special
        ]
        return "".join(tokens)


def build_toy_tokenizer() -> ToyTokenizer:
    # 最小可运行词表：包含示例句子字符 + 常用特殊符号
    vocab = [
        "<pad>",
        "<bos>",
        "<eos>",
        "<unk>",
        "我",
        "爱",
        "北",
        "京",
        "天",
        "安",
        "门",
    ]
    token_to_id = {tok: idx for idx, tok in enumerate(vocab)}
    return ToyTokenizer(token_to_id=token_to_id)


def load_model(
    tokenizer: ToyTokenizer,
    ckpt_path: str | None,
    device: torch.device,
) -> Transformer:
    vocab_size = len(tokenizer.token_to_id)
    model = Transformer(
        src_vocab_size=vocab_size,
        tgt_vocab_size=vocab_size,
        d_model=128,
        num_layers=2,
        num_heads=4,
        d_ff=256,
        dropout=0.0,
        max_len=256,
        pad_idx=tokenizer.pad_id,
    ).to(device)

    if ckpt_path:
        ckpt_file = Path(ckpt_path)
        if not ckpt_file.exists():
            raise FileNotFoundError(f"checkpoint 不存在: {ckpt_file}")
        state = torch.load(ckpt_file, map_location=device)
        # 兼容 {"state_dict": ...} 或直接 state_dict 两种格式
        state_dict = state.get("state_dict", state) if isinstance(state, dict) else state
        model.load_state_dict(state_dict, strict=True)
        print(f"[INFO] 已加载 checkpoint: {ckpt_file}")
    else:
        print("[WARN] 未提供 checkpoint，当前输出仅用于演示推理流程。")

    model.eval()
    return model


@torch.no_grad()
def greedy_decode(
    model: Transformer,
    src_tokens: torch.Tensor,
    bos_id: int,
    eos_id: int,
    max_new_tokens: int,
) -> torch.Tensor:
    """
    自回归贪心解码：
    - 初始 tgt = [<bos>]
    - 每轮调用 model(src, tgt)，取最后一个位置 argmax 作为新 token
    - 追加到 tgt，直到 <eos> 或达到 max_new_tokens
    """
    device = src_tokens.device
    tgt_tokens = torch.tensor([[bos_id]], dtype=torch.long, device=device)  # [1, 1]

    for step in range(1, max_new_tokens + 1):
        logits = model(src_tokens, tgt_tokens)         # [1, Lt, V]
        next_token = logits[:, -1, :].argmax(dim=-1)  # [1]
        next_token = next_token.unsqueeze(1)           # [1, 1]

        tgt_tokens = torch.cat([tgt_tokens, next_token], dim=1)  # [1, Lt+1]
        print(f"[STEP {step:02d}] tgt_token_ids = {tgt_tokens.squeeze(0).tolist()}")

        if int(next_token.item()) == eos_id:
            break

    return tgt_tokens


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transformer 自回归推理示例")
    parser.add_argument(
        "--text",
        type=str,
        default="我爱北京",
        help="输入文本（源序列）",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=12,
        help="最多新生成 token 数",
    )
    parser.add_argument(
        "--ckpt",
        type=str,
        default=None,
        help="可选：模型 checkpoint 路径",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer = build_toy_tokenizer()
    model = load_model(tokenizer, args.ckpt, device)

    src_ids = tokenizer.encode(args.text)
    if not src_ids:
        raise ValueError("输入文本为空，无法推理。")

    src_tokens = torch.tensor([src_ids], dtype=torch.long, device=device)  # [1, Ls]

    print("=" * 60)
    print(f"输入文本: {args.text}")
    print(f"src_token_ids: {src_ids}")
    print(f"src_tokens shape: {tuple(src_tokens.shape)}")
    print(f"device: {device}")
    print("=" * 60)

    out_tgt = greedy_decode(
        model=model,
        src_tokens=src_tokens,
        bos_id=tokenizer.bos_id,
        eos_id=tokenizer.eos_id,
        max_new_tokens=args.max_new_tokens,
    )

    out_ids = out_tgt.squeeze(0).tolist()
    out_text = tokenizer.decode(out_ids)

    print("=" * 60)
    print(f"最终 tgt_token_ids: {out_ids}")
    print(f"解码结果(去掉特殊符号): {out_text}")
    print("=" * 60)


if __name__ == "__main__":
    main()
