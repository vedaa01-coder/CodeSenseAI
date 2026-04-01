import numpy as np
import faiss

def build_index(vectors):
    vecs = np.array(vectors, dtype="float32")
    dim = vecs.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vecs)
    return index, dim

def search_index(index, query_vector, k=5):
    q = np.array([query_vector], dtype="float32")
    D, I = index.search(q, k)
    return D[0].tolist(), I[0].tolist()