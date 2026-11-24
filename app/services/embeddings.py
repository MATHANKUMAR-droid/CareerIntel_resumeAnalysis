"""Optional sentence-transformer embeddings with deterministic TF-IDF fallback."""
import numpy as np
class Embedder:
 def __init__(self):
  self.model=None
  try:
   from sentence_transformers import SentenceTransformer
   self.model=SentenceTransformer('all-MiniLM-L6-v2')
  except Exception:pass
 def encode(self,texts:list[str])->np.ndarray:
  if self.model is not None:return np.asarray(self.model.encode(texts,normalize_embeddings=True))
  from sklearn.feature_extraction.text import TfidfVectorizer
  if not texts:return np.zeros((0,0))
  return TfidfVectorizer(ngram_range=(1,2)).fit_transform(texts).toarray()
