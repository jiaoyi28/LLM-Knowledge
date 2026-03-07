"""
批量推理 + Beam Search 示例。

用法示例：
    python inference_batch_beam.py
    python inference_batch_beam.py --mode greedy --texts 我爱北京 我爱北
    python inference_batch_beam.py --mode beam --beam-size 4 --max-new-tokens 6
    python inference_batch_beam.py --ckpt transformer_ckpt.pt

说明：
1) 该脚本演示“推理流程”；若未加载训练权重，输出仅供流程验证；
2) greedy 模式支持真正 batch 同时解码；
3) beam 模式为“批量入口 + 样本级束搜索”（逐条样本执行 beam）；
4) 在训练充分时，示例输入“我爱北京”可生成“天安门”。
"""

from __future__ import annotations

import argparse
from typing import List, Sequence, Tuple

import torch
import torch.nn.functional as F

from inference_demo import build_toy_tokenizer, load_model
from transformer import Transformer


def pad_to_batch(sequences: Sequence[List[int]], pad_id: int, device: torch.device) -> torch.Tensor:
    max_len = max(len(x) for x in sequences)
    rows: List[List[int]] = []
    for ids in sequences:
        rows.append(ids + [pad_id] * (max_len - len(ids)))
    return torch.tensor(rows, dtype=torch.long, device=device)  # [B, L]


@torch.no_grad()
def greedy_decode_batch(
    model: Transformer,
    src_tokens: torch.Tensor,
    bos_id: int,
    eos_id: int,
    max_new_tokens: int,
) -> torch.Tensor:
    """
    真正 batch 的自回归贪心解码。

    Args:
        src_tokens: [B, Ls]
    Returns:
        tgt_tokens: [B, Lt]
    """
    batch_size = src_tokens.size(0)
    tgt_tokens = torch.full(
        (batch_size, 1),
        fill_value=bos_id,
        dtype=torch.long,
        device=src_tokens.device,
    )  # [B, 1]

    finished = torch.zeros(batch_size, dtype=torch.bool, device=src_tokens.device)

    for _ in range(max_new_tokens):
        logits = model(src_tokens, tgt_tokens)  # [B, Lt, V]
        next_token = logits[:, -1, :].argmax(dim=-1)  # [B]
        next_token = torch.where(
            finished,
            torch.full_like(next_token, eos_id),
            next_token,
        )
        tgt_tokens = torch.cat([tgt_tokens, next_token.unsqueeze(1)], dim=1)
        finished = finished | (next_token == eos_id)
        if bool(finished.all()):
            break

    return tgt_tokens


def _length_penalty(length: int, alpha: float) -> float:
    return ((5.0 + float(length)) / 6.0) ** alpha


@torch.no_grad()
def beam_search_single(
    model: Transformer,
    src_single: torch.Tensor,
    bos_id: int,
    eos_id: int,
    beam_size: int,
    max_new_tokens: int,
    alpha: float,
) -> torch.Tensor:
    """
    单样本 Beam Search。

    Args:
        src_single: [1, Ls]
    Returns:
        best_tokens: [1, Lt]
    """
    beams: List[Tuple[torch.Tensor, float, bool]] = [
        (torch.tensor([[bos_id]], dtype=torch.long, device=src_single.device), 0.0, False)
    ]

    for _ in range(max_new_tokens):
        all_candidates: List[Tuple[torch.Tensor, float, bool]] = []

        for tokens, score, ended in beams:
            if ended:
                all_candidates.append((tokens, score, True))
                continue

            logits = model(src_single, tokens)  # [1, Lt, V]
            log_probs = F.log_softmax(logits[:, -1, :], dim=-1)  # [1, V]
            topk_log_probs, topk_ids = torch.topk(log_probs, k=beam_size, dim=-1)

            for k in range(beam_size):
                token_id = int(topk_ids[0, k].item())
                token_log_prob = float(topk_log_probs[0, k].item())
                new_tokens = torch.cat(
                    [
                        tokens,
                        torch.tensor([[token_id]], dtype=torch.long, device=src_single.device),
                    ],
                    dim=1,
                )
                new_score = score + token_log_prob
                is_ended = token_id == eos_id
                all_candidates.append((new_tokens, new_score, is_ended))

        def rank_key(item: Tuple[torch.Tensor, float, bool]) -> float:
            tokens, score, _ = item
            length = max(1, tokens.size(1) - 1)  # 去掉 <bos> 的长度
            return score / _length_penalty(length, alpha)

        all_candidates.sort(key=rank_key, reverse=True)
        beams = all_candidates[:beam_size]

        if all(flag for _, _, flag in beams):
            break

    best = max(
        beams,
        key=lambda x: x[1] / _length_penalty(max(1, x[0].size(1) - 1), alpha),
    )
    return best[0]


@torch.no_grad()
def beam_decode_batch(
    model: Transformer,
    src_tokens: torch.Tensor,
    bos_id: int,
    eos_id: int,
    beam_size: int,
    max_new_tokens: int,
    alpha: float,
) -> List[torch.Tensor]:
    """
    批量入口的 beam：逐条样本执行束搜索。

    Args:
        src_tokens: [B, Ls]
    Returns:
        每条样本的 best sequence（元素形状均为 [1, Lt]）
    """
    outputs: List[torch.Tensor] = []
    for i in range(src_tokens.size(0)):
        src_single = src_tokens[i : i + 1]
        out = beam_search_single(
            model=model,
            src_single=src_single,
            bos_id=bos_id,
            eos_id=eos_id,
            beam_size=beam_size,
            max_new_tokens=max_new_tokens,
            alpha=alpha,
        )
        outputs.append(out)
    return outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量推理 + Beam Search 示例")
    parser.add_argument(
        "--texts",
        nargs="+",
        default=["我爱北京", "我爱北"],
        help="批量输入文本（空格分隔）",
    )
    parser.add_argument(
        "--mode",
        choices=["greedy", "beam"],
        default="beam",
        help="推理模式：greedy 或 beam",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=4,
        help="beam 模式下的束宽",
    )
    parser.add_argument(
        "--length-penalty-alpha",
        type=float,
        default=0.6,
        help="beam 的长度惩罚系数 alpha，0 表示不惩罚",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=6,
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

    src_id_list = [tokenizer.encode(text) for text in args.texts]
    if any(len(x) == 0 for x in src_id_list):
        raise ValueError("检测到空文本，请移除空输入后重试。")

    src_tokens = pad_to_batch(src_id_list, tokenizer.pad_id, device)

    print("=" * 72)
    print(f"mode: {args.mode}")
    print(f"batch_size: {src_tokens.size(0)}")
    print(f"src_tokens shape: {tuple(src_tokens.shape)}")
    print("=" * 72)

    for idx, (text, ids) in enumerate(zip(args.texts, src_id_list)):
        print(f"[SRC {idx}] text={text} | token_ids={ids}")

    print("=" * 72)

    if args.mode == "greedy":
        out = greedy_decode_batch(
            model=model,
            src_tokens=src_tokens,
            bos_id=tokenizer.bos_id,
            eos_id=tokenizer.eos_id,
            max_new_tokens=args.max_new_tokens,
        )  # [B, Lt]

        for i in range(out.size(0)):
            ids = out[i].tolist()
            text = tokenizer.decode(ids)
            print(f"[OUT {i}] tgt_token_ids={ids}")
            print(f"[OUT {i}] decoded={text}")
    else:
        out_list = beam_decode_batch(
            model=model,
            src_tokens=src_tokens,
            bos_id=tokenizer.bos_id,
            eos_id=tokenizer.eos_id,
            beam_size=args.beam_size,
            max_new_tokens=args.max_new_tokens,
            alpha=args.length_penalty_alpha,
        )
        for i, out in enumerate(out_list):
            ids = out.squeeze(0).tolist()
            text = tokenizer.decode(ids)
            print(f"[OUT {i}] tgt_token_ids={ids}")
            print(f"[OUT {i}] decoded={text}")

    print("=" * 72)


if __name__ == "__main__":
    main()
