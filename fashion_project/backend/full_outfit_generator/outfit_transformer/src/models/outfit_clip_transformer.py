import torch
from torch import nn
from typing import List, Tuple, Union
from dataclasses import dataclass
import numpy as np

from ..data.datatypes import FashionItem, FashionCompatibilityQuery
from .modules.encoder import CLIPItemEncoder
from .outfit_transformer import OutfitTransformer, OutfitTransformerConfig

@dataclass
class OutfitCLIPTransformerConfig(OutfitTransformerConfig):
    item_enc_clip_model_name: str = "patrickjohncyh/fashion-clip"

class OutfitCLIPTransformer(OutfitTransformer):

    def __init__(self, cfg: OutfitCLIPTransformerConfig = OutfitCLIPTransformerConfig()):
        super().__init__(cfg)

        # === CATEGORY-ATTENTION MODULES ===
        self.num_categories = 11  # semantic categories
        self.d_embed = self.item_enc.d_embed
        self.num_heads = 4

        self.category_prototypes = nn.Parameter(
            torch.randn(self.num_categories, self.d_embed) * 0.02
        )

        self.category_attn = nn.MultiheadAttention(
            embed_dim=self.d_embed,
            num_heads=self.num_heads,
            batch_first=True
        )

    def _init_item_enc(self) -> CLIPItemEncoder:
        self.item_enc = CLIPItemEncoder(
            model_name=self.cfg.item_enc_clip_model_name,
            enc_norm_out=self.cfg.item_enc_norm_out,
            aggregation_method=self.cfg.aggregation_method
        )

    def predict_score(self, query: List[FashionCompatibilityQuery], use_precomputed_embedding: bool = False) -> torch.Tensor:
        outfits = [q.outfit for q in query]
        if use_precomputed_embedding:
            assert all([item.embedding is not None for item in sum(outfits, [])])
            embs_of_inputs = [[item.embedding for item in outfit] for outfit in outfits]
            embs_of_inputs, mask = self._pad_and_mask_for_embs(embs_of_inputs)
        else:
            images, texts, mask = self._pad_and_mask_for_outfits(outfits)
            embs_of_inputs = self.item_enc(images, texts)

        # === Add task embedding ===
        task_emb = torch.cat([self.task_emb, self.predict_emb], dim=-1)
        embs_of_inputs = torch.cat([
            task_emb.view(1, 1, -1).expand(len(query), -1, -1),
            embs_of_inputs
        ], dim=1)
        mask = torch.cat([
            torch.zeros(len(query), 1, dtype=torch.bool, device=self.device),
            mask
        ], dim=1)

        # === Transformer Encoder ===
        last_hidden_states = self._style_enc_forward(embs_of_inputs, src_key_padding_mask=mask)
        item_embs = last_hidden_states[:, 1:, :]  # (B, L, D)

        B, L, D = item_embs.shape
        category_keys = self.category_prototypes.unsqueeze(0).expand(B, -1, -1)  # (B, C, D)

        # === Multi-Head Attention: item_embs attend to category prototypes ===
        attn_output, _ = self.category_attn(
            query=item_embs,
            key=category_keys,
            value=category_keys
        )

        item_embs = item_embs + attn_output  # (B, L, D)
        outfit_emb = item_embs.mean(dim=1)   # (B, D)

        scores = self.predict_ffn(outfit_emb)  # (B, 1)
        return scores

    def precompute_clip_embedding(self, item: List[FashionItem]) -> np.ndarray:
        outfits = [[item_] for item_ in item]
        images, texts, mask = self._pad_and_mask_for_outfits(outfits)
        enc_outs = self.item_enc(images, texts)  # [B, 1, D]
        embeddings = enc_outs[:, 0, :]  # [B, D]
        return embeddings.detach().cpu().numpy()