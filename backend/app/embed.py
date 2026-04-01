from sentence_transformers import SentenceTransformer
from .config import settings

model = SentenceTransformer(settings.EMBED_MODEL_NAME)

def embed_texts(texts):
    vectors = model.encode(texts, normalize_embeddings=True)
    return vectors.tolist()