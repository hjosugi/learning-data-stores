"""Embedded vector store with toy embeddings, pure python3 stdlib (no numpy).

This is the Dockerless learning substitute for LanceDB / Chroma. It builds the
core ideas behind a vector database from scratch so the concepts are visible:

- embedding storage: each document is turned into a fixed-dimension vector
- dense vector (cosine) search: rank by cosine similarity of L2-normalized vectors
- metadata filtering: restrict candidates by tag/category before ranking
- hybrid search: blend keyword overlap with cosine similarity
- upsert / delete: mutate the collection by stable document id

The "embedding model" here is a deterministic toy: we hash each token into a
bucket and count it (bag-of-hashed-tokens), then L2-normalize. Real systems call
an embedding model (sentence-transformers, OpenAI, Cohere, Workers AI, etc.) to
get semantically meaningful vectors. The *store mechanics* you learn here map
one-to-one onto LanceDB and Chroma; only the vector source changes.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Callable, Iterable

# Dimension of the toy embedding space. Small enough to inspect by hand, large
# enough that distinct vocabularies rarely collide into identical vectors.
EMBED_DIM = 64

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Lowercase and split into alphanumeric tokens. Deterministic."""
    return _TOKEN_RE.findall(text.lower())


def _stable_hash(token: str) -> int:
    """Deterministic non-cryptographic hash for a token.

    Python's built-in hash() is salted per-process, so it is NOT reproducible
    across runs. We need determinism so the same corpus always yields the same
    vectors (and so tests are stable), hence this small FNV-1a implementation.
    """
    h = 0x811C9DC5  # FNV offset basis (32-bit)
    for ch in token.encode("utf-8"):
        h ^= ch
        h = (h * 0x01000193) & 0xFFFFFFFF  # FNV prime, keep 32-bit
    return h


def embed(text: str, dim: int = EMBED_DIM) -> list[float]:
    """Toy embedding: bag-of-hashed-tokens, then L2-normalize.

    Each token is hashed into one of `dim` buckets and its count is added there.
    The result is L2-normalized so that cosine similarity == dot product, which
    keeps the search code simple. An empty / unknown document yields a zero
    vector (cosine similarity with anything is then 0).
    """
    vector = [0.0] * dim
    for token in tokenize(text):
        vector[_stable_hash(token) % dim] += 1.0
    return l2_normalize(vector)


def l2_normalize(vector: list[float]) -> list[float]:
    """Scale a vector to unit length. A zero vector is returned unchanged."""
    norm = math.sqrt(sum(component * component for component in vector))
    if norm == 0.0:
        return vector
    return [component / norm for component in vector]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity of two equal-length vectors.

    For already-normalized vectors this equals the dot product, but we divide by
    the norms anyway so the function is correct for any input vectors.
    """
    if len(a) != len(b):
        raise ValueError("vectors must have the same dimension")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def keyword_overlap(query: str, text: str) -> float:
    """Jaccard-style keyword overlap in [0, 1] between query and document.

    This is a tiny stand-in for a real full-text/BM25 lexical score. It rewards
    exact token matches that dense embeddings can blur, which is the whole point
    of hybrid search.
    """
    query_tokens = set(tokenize(query))
    text_tokens = set(tokenize(text))
    if not query_tokens or not text_tokens:
        return 0.0
    intersection = query_tokens & text_tokens
    union = query_tokens | text_tokens
    return len(intersection) / len(union)


@dataclass
class Document:
    """A stored record: id, raw text, metadata, and its cached embedding."""

    id: str
    text: str
    metadata: dict[str, object]
    vector: list[float]


@dataclass
class SearchHit:
    """A ranked search result with the scores that produced the ranking."""

    id: str
    text: str
    metadata: dict[str, object]
    score: float
    cosine: float
    keyword: float


# A metadata filter is any predicate over a document's metadata dict.
MetadataFilter = Callable[[dict[str, object]], bool]


@dataclass
class VectorStore:
    """An in-memory embedded vector store, keyed by stable document id.

    Mirrors the surface of LanceDB / Chroma collections: upsert, delete, and
    search with optional metadata filtering and hybrid scoring.
    """

    dim: int = EMBED_DIM
    _documents: dict[str, Document] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self._documents)

    def upsert(self, id: str, text: str, metadata: dict[str, object] | None = None) -> None:
        """Insert a new document or overwrite an existing one by id.

        Re-embeds the text every call so an upsert always reflects the latest
        text/metadata. Same name and idempotent semantics as Chroma's upsert.
        """
        self._documents[id] = Document(
            id=id,
            text=text,
            metadata=dict(metadata or {}),
            vector=embed(text, self.dim),
        )

    def delete(self, id: str) -> bool:
        """Remove a document by id. Returns True if something was removed."""
        return self._documents.pop(id, None) is not None

    def get(self, id: str) -> Document | None:
        return self._documents.get(id)

    def search(
        self,
        query: str,
        k: int = 3,
        metadata_filter: MetadataFilter | None = None,
        hybrid_alpha: float = 1.0,
    ) -> list[SearchHit]:
        """Return the top-k documents for a query.

        - metadata_filter: predicate applied BEFORE ranking (pre-filter), so
          excluded documents can never appear in the results. This is the cheap,
          correct default; real vector DBs also offer post-filtering.
        - hybrid_alpha: blend weight in [0, 1].
            score = alpha * cosine + (1 - alpha) * keyword_overlap
          alpha = 1.0 -> pure dense vector search.
          alpha = 0.0 -> pure keyword search.
          0 < alpha < 1 -> hybrid search.

        Ties are broken by id so ordering is deterministic.
        """
        if not 0.0 <= hybrid_alpha <= 1.0:
            raise ValueError("hybrid_alpha must be in [0, 1]")

        query_vector = embed(query, self.dim)
        hits: list[SearchHit] = []
        for document in self._documents.values():
            if metadata_filter is not None and not metadata_filter(document.metadata):
                continue  # pre-filter: never reaches ranking
            cosine = cosine_similarity(query_vector, document.vector)
            keyword = keyword_overlap(query, document.text)
            score = hybrid_alpha * cosine + (1.0 - hybrid_alpha) * keyword
            hits.append(
                SearchHit(
                    id=document.id,
                    text=document.text,
                    metadata=document.metadata,
                    score=score,
                    cosine=cosine,
                    keyword=keyword,
                )
            )

        hits.sort(key=lambda hit: (-hit.score, hit.id))
        return hits[:k]


def sample_corpus() -> list[tuple[str, str, dict[str, object]]]:
    """A small, hand-written corpus of (id, text, metadata) tuples.

    The texts are chosen so that keyword vs semantic-ish overlap differs, which
    makes the hybrid-search demo and tests meaningful.
    """
    return [
        ("doc-1", "cats and dogs are common household pets", {"category": "animals", "tags": ["pets"]}),
        ("doc-2", "lions tigers and leopards are wild big cats", {"category": "animals", "tags": ["wild"]}),
        ("doc-3", "python is a high level programming language", {"category": "tech", "tags": ["code"]}),
        ("doc-4", "rust and go are systems programming languages", {"category": "tech", "tags": ["code"]}),
        ("doc-5", "vector databases store embeddings for similarity search", {"category": "tech", "tags": ["db"]}),
        ("doc-6", "espresso and cappuccino are popular coffee drinks", {"category": "food", "tags": ["drink"]}),
    ]


def build_sample_store() -> VectorStore:
    """Build and populate a store from the sample corpus via upsert."""
    store = VectorStore()
    for id, text, metadata in sample_corpus():
        store.upsert(id, text, metadata)
    return store


def has_category(category: str) -> MetadataFilter:
    """Convenience metadata filter: keep documents in one category."""
    return lambda metadata: metadata.get("category") == category


def demo() -> dict[str, object]:
    """Run the two Definition-of-Done queries and return a small result dict.

    1. insert/load query: build the store and read one document back by id.
    2. read/search query: a hybrid, metadata-filtered nearest-neighbour search.
    """
    store = build_sample_store()

    # (1) insert/load query: load a document by its id after upserting.
    loaded = store.get("doc-5")
    insert_load = {
        "count": len(store),
        "loaded_id": loaded.id if loaded else None,
        "loaded_text": loaded.text if loaded else None,
    }

    # (2) read/search query: hybrid search restricted to the 'tech' category.
    hits = store.search(
        "programming language",
        k=2,
        metadata_filter=has_category("tech"),
        hybrid_alpha=0.5,
    )
    read_search = [
        {"id": hit.id, "score": round(hit.score, 4), "cosine": round(hit.cosine, 4), "keyword": round(hit.keyword, 4)}
        for hit in hits
    ]

    return {"insert_load": insert_load, "read_search": read_search}


def main() -> None:
    result = demo()

    insert_load = result["insert_load"]
    print("insert/load query:")
    print(f"  documents in store = {insert_load['count']}")
    print(f"  loaded {insert_load['loaded_id']!r} -> {insert_load['loaded_text']!r}")

    print("read/search query (hybrid, category='tech', k=2):")
    for rank, hit in enumerate(result["read_search"], start=1):
        print(
            f"  {rank}. {hit['id']} "
            f"score={hit['score']} cosine={hit['cosine']} keyword={hit['keyword']}"
        )


if __name__ == "__main__":
    main()
