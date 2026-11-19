"""FlagEmbedding + Transformers v5 兼容补丁

现象：BGEM3.encode_single_device（FlagEmbedding 1.4.x）把 return_colbert
等模型级参数透传给 pad_with_compat → tokenizer.pad，Transformers v5 的
PreTrainedTokenizerBase.pad 不接受这些参数而抛 TypeError，导致
/v1/embeddings 500。

处理：包装 pad_with_compat，过滤 tokenizer.pad 不支持的键；由于各 inference
模块以 `from ... import pad_with_compat` 方式绑定，需同步替换其模块属性。
须在引擎加载模型前调用（create_app 阶段）。
"""
import importlib

_PAD_ALLOWED = {
    "padding", "truncation", "max_length", "return_tensors",
    "return_attention_mask", "return_token_type_ids", "verbose",
    "pad_to_multiple_of", "return_overflowing_tokens",
    "return_special_tokens_mask",
}

_MODULES = (
    "inference.embedder.encoder_only.m3",
    "inference.embedder.encoder_only.base",
    "inference.embedder.decoder_only.icl",
    "inference.embedder.decoder_only.pseudo_moe",
    "inference.embedder.decoder_only.base",
    "inference.reranker.encoder_only.base",
    "inference.reranker.decoder_only.base",
    "inference.reranker.decoder_only.lightweight",
)


def install_flagembedding_pad_patch() -> bool:
    try:
        from FlagEmbedding.utils import tokenizer_compat
    except Exception:
        return False

    orig = tokenizer_compat.pad_with_compat

    def pad_with_compat(tokenizer, encoded_inputs, **kwargs):
        return orig(tokenizer, encoded_inputs,
                    **{k: v for k, v in kwargs.items() if k in _PAD_ALLOWED})

    tokenizer_compat.pad_with_compat = pad_with_compat
    patched = 0
    for name in _MODULES:
        try:
            mod = importlib.import_module("FlagEmbedding." + name)
            if getattr(mod, "pad_with_compat", None) is orig:
                mod.pad_with_compat = pad_with_compat
                patched += 1
        except Exception:
            pass
    return True
