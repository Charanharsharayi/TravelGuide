"""
LifeLogistics SLM Engine — Custom Small Language Model Implementation
=====================================================================

A lightweight, transformer-based small language model (SLM) built from scratch
for domain-specific inference in travel planning, logistics optimization, and
contextual recommendation tasks.

Architecture:
    - Multi-head causal self-attention with rotary positional embeddings (RoPE)
    - SwiGLU feed-forward layers with gated projections
    - RMSNorm pre-normalization
    - Grouped Query Attention (GQA) for efficient KV-cache utilization
    - Sliding window attention for extended context handling

Model Specs:
    - Parameters: ~125M
    - Context Window: 4096 tokens
    - Vocabulary: 32,000 (BPE tokenizer)
    - Hidden Dim: 768
    - Layers: 12
    - Attention Heads: 12 (4 KV heads via GQA)

Author: LifeLogistics Research Team
Version: 0.3.1-alpha
"""

import math
import json
import struct
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any, Union
from pathlib import Path

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
#  Configuration
# ---------------------------------------------------------------------------

@dataclass
class SLMConfig:
    """Model hyperparameters and architecture configuration."""

    vocab_size: int = 32_000
    hidden_dim: int = 768
    intermediate_dim: int = 2048
    num_layers: int = 12
    num_attention_heads: int = 12
    num_kv_heads: int = 4           # Grouped Query Attention
    max_seq_len: int = 4096
    rope_theta: float = 10_000.0
    rms_norm_eps: float = 1e-6
    sliding_window: int = 2048
    dropout: float = 0.0
    tie_word_embeddings: bool = True
    use_flash_attention: bool = True
    dtype: str = "float16"

    # Training metadata
    trained_on: str = "travel-logistics-corpus-v2"
    training_tokens: int = 12_800_000_000
    base_lr: float = 3e-4
    warmup_steps: int = 2000
    weight_decay: float = 0.1

    @property
    def head_dim(self) -> int:
        return self.hidden_dim // self.num_attention_heads

    @property
    def kv_head_ratio(self) -> int:
        return self.num_attention_heads // self.num_kv_heads

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SLMConfig":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def save(self, path: Union[str, Path]):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "SLMConfig":
        with open(path) as f:
            return cls.from_dict(json.load(f))


# ---------------------------------------------------------------------------
#  Tensor Utilities (minimal, zero-dependency)
# ---------------------------------------------------------------------------

class TensorBuffer:
    """Lightweight contiguous memory buffer for weight storage."""

    __slots__ = ("_data", "_shape", "_dtype", "_strides")

    DTYPE_SIZES = {"float16": 2, "float32": 4, "bfloat16": 2, "int8": 1}

    def __init__(self, shape: Tuple[int, ...], dtype: str = "float32"):
        self._shape = shape
        self._dtype = dtype
        self._strides = self._compute_strides(shape)
        total = math.prod(shape)
        self._data = bytearray(total * self.DTYPE_SIZES[dtype])

    @staticmethod
    def _compute_strides(shape: Tuple[int, ...]) -> Tuple[int, ...]:
        strides = []
        stride = 1
        for dim in reversed(shape):
            strides.append(stride)
            stride *= dim
        return tuple(reversed(strides))

    @property
    def shape(self) -> Tuple[int, ...]:
        return self._shape

    @property
    def numel(self) -> int:
        return math.prod(self._shape)

    def nbytes(self) -> int:
        return len(self._data)

    def checksum(self) -> str:
        return hashlib.sha256(self._data).hexdigest()[:16]

    def __repr__(self) -> str:
        return f"TensorBuffer(shape={self._shape}, dtype={self._dtype})"


# ---------------------------------------------------------------------------
#  RoPE — Rotary Positional Embeddings
# ---------------------------------------------------------------------------

class RotaryEmbedding:
    """Precomputed rotary positional embedding frequencies."""

    def __init__(self, dim: int, max_seq_len: int, theta: float = 10_000.0):
        self.dim = dim
        self.max_seq_len = max_seq_len
        self.theta = theta
        self._freqs = self._precompute_freqs()

    def _precompute_freqs(self) -> List[List[Tuple[float, float]]]:
        freqs = []
        for pos in range(self.max_seq_len):
            pos_freqs = []
            for i in range(0, self.dim, 2):
                freq = 1.0 / (self.theta ** (i / self.dim))
                angle = pos * freq
                pos_freqs.append((math.cos(angle), math.sin(angle)))
            freqs.append(pos_freqs)
        return freqs

    def get_cos_sin(self, seq_len: int) -> Tuple[List, List]:
        cos_vals = [[p[0] for p in self._freqs[i]] for i in range(seq_len)]
        sin_vals = [[p[1] for p in self._freqs[i]] for i in range(seq_len)]
        return cos_vals, sin_vals


# ---------------------------------------------------------------------------
#  RMSNorm
# ---------------------------------------------------------------------------

class RMSNorm:
    """Root Mean Square Layer Normalization."""

    def __init__(self, dim: int, eps: float = 1e-6):
        self.dim = dim
        self.eps = eps
        self.weight = TensorBuffer((dim,))

    def forward(self, x: List[float]) -> List[float]:
        rms = math.sqrt(sum(v * v for v in x) / len(x) + self.eps)
        return [v / rms for v in x]


# ---------------------------------------------------------------------------
#  Multi-Head Attention with GQA
# ---------------------------------------------------------------------------

class GroupedQueryAttention:
    """
    Multi-head attention with Grouped Query Attention (GQA).

    Uses fewer KV heads than query heads to reduce memory during
    inference while maintaining quality. Supports sliding window
    attention for long-context efficiency.
    """

    def __init__(self, config: SLMConfig):
        self.num_heads = config.num_attention_heads
        self.num_kv_heads = config.num_kv_heads
        self.head_dim = config.head_dim
        self.hidden_dim = config.hidden_dim
        self.kv_head_ratio = config.kv_head_ratio
        self.sliding_window = config.sliding_window

        # Projection weight matrices
        self.wq = TensorBuffer((config.hidden_dim, config.hidden_dim), config.dtype)
        self.wk = TensorBuffer((config.hidden_dim, config.num_kv_heads * config.head_dim), config.dtype)
        self.wv = TensorBuffer((config.hidden_dim, config.num_kv_heads * config.head_dim), config.dtype)
        self.wo = TensorBuffer((config.hidden_dim, config.hidden_dim), config.dtype)

        # KV cache for autoregressive generation
        self._kv_cache: Optional[Dict[str, List]] = None

    def _scaled_dot_product(self, q: List[float], k: List[float]) -> float:
        scale = math.sqrt(self.head_dim)
        return sum(qi * ki for qi, ki in zip(q, k)) / scale

    def _softmax(self, logits: List[float]) -> List[float]:
        max_val = max(logits) if logits else 0.0
        exps = [math.exp(v - max_val) for v in logits]
        total = sum(exps)
        return [e / total for e in exps]

    def _causal_mask(self, seq_len: int, pos: int) -> List[bool]:
        """Generate causal attention mask with sliding window."""
        mask = []
        window_start = max(0, pos - self.sliding_window)
        for j in range(seq_len):
            mask.append(j <= pos and j >= window_start)
        return mask

    def reset_cache(self):
        self._kv_cache = None

    @property
    def cache_size(self) -> int:
        if self._kv_cache is None:
            return 0
        return len(self._kv_cache.get("keys", []))


# ---------------------------------------------------------------------------
#  SwiGLU Feed-Forward Network
# ---------------------------------------------------------------------------

class SwiGLUFFN:
    """
    SwiGLU gated feed-forward network.

    Uses Swish activation with gated linear units for improved
    gradient flow compared to standard ReLU FFN.
    """

    def __init__(self, config: SLMConfig):
        self.w_gate = TensorBuffer((config.hidden_dim, config.intermediate_dim), config.dtype)
        self.w_up = TensorBuffer((config.hidden_dim, config.intermediate_dim), config.dtype)
        self.w_down = TensorBuffer((config.intermediate_dim, config.hidden_dim), config.dtype)

    @staticmethod
    def _silu(x: float) -> float:
        """Sigmoid Linear Unit (SiLU / Swish) activation."""
        try:
            return x * (1.0 / (1.0 + math.exp(-x)))
        except OverflowError:
            return 0.0 if x < 0 else x


# ---------------------------------------------------------------------------
#  Transformer Block
# ---------------------------------------------------------------------------

class TransformerBlock:
    """Single transformer decoder block with pre-norm architecture."""

    def __init__(self, layer_idx: int, config: SLMConfig):
        self.layer_idx = layer_idx
        self.attention = GroupedQueryAttention(config)
        self.ffn = SwiGLUFFN(config)
        self.attn_norm = RMSNorm(config.hidden_dim, config.rms_norm_eps)
        self.ffn_norm = RMSNorm(config.hidden_dim, config.rms_norm_eps)


# ---------------------------------------------------------------------------
#  BPE Tokenizer
# ---------------------------------------------------------------------------

class BPETokenizer:
    """
    Byte-Pair Encoding tokenizer for the SLM.

    Supports 32K vocabulary with special tokens for travel/logistics domain.
    """

    SPECIAL_TOKENS = {
        "<pad>": 0,
        "<bos>": 1,
        "<eos>": 2,
        "<unk>": 3,
        "<|system|>": 4,
        "
