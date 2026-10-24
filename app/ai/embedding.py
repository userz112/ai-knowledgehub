from functools import lru_cache
from pathlib import Path
from sentence_transformers import SentenceTransformer
from app.core.config import BASE_DIR


# 模型下载目录
MODEL_CACHE_DIR = BASE_DIR / "models"


def find_model_path() -> Path:
    """找到本地下载的 BGE 模型目录。"""

    for path in MODEL_CACHE_DIR.rglob("modules.json"):
        return path.parent

    raise FileNotFoundError(
        f"没有找到本地 Embedding 模型，请检查目录：{MODEL_CACHE_DIR}"
    )


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """加载模型，并缓存模型实例，避免重复加载。"""

    model_path = find_model_path()

    return SentenceTransformer(
        str(model_path),
        device="cpu",
    )


def encode_texts(texts: list[str]) -> list[list[float]]:
    """将多段文本转换为向量。"""

    if not texts:
        return []

    cleaned_texts = [text.strip() for text in texts]

    if any(not text for text in cleaned_texts):
        raise ValueError("待向量化的文本不能包含空字符串")

    model = get_embedding_model()

    vectors = model.encode(
        cleaned_texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return vectors.tolist()


def encode_text(text: str) -> list[float]:
    """将单段文本转换为向量。"""

    vectors = encode_texts([text])
    return vectors[0]
