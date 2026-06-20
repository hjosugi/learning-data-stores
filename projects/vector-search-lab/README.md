# Vector Search Lab

An embedded vector store built from scratch with **python3 standard library only
(no numpy)**. It is the Dockerless learning substitute for LanceDB and Chroma:
the *store mechanics* are real, only the embedding source is a toy.

It demonstrates the named concepts behind a vector database:

- **embedding storage** — each document is turned into a fixed-dimension vector
  and cached alongside its text and metadata
- **dense vector (cosine) search** — rank documents by cosine similarity of
  L2-normalized vectors
- **metadata filtering** — restrict candidates by tag/category before ranking
- **hybrid full-text + vector search** — blend keyword overlap with cosine score
- **upsert / delete** — mutate the collection by stable document id

The "embedding model" is deterministic and pure-python: each token is hashed
into a bucket and counted (bag-of-hashed-tokens), then the vector is
L2-normalized so cosine similarity equals the dot product. Real systems replace
this with an embedding model; everything else maps directly to a real vector DB.

Last verified: 2026-06-21

## Run

```bash
python3 projects/vector-search-lab/app.py
```

Expected output (the two Definition-of-Done queries):

```text
insert/load query:
  documents in store = 6
  loaded 'doc-5' -> 'vector databases store embeddings for similarity search'
read/search query (hybrid, category='tech', k=2):
  1. doc-3 score=0.4101 cosine=0.5345 keyword=0.2857
  2. doc-4 score=0.1961 cosine=0.2673 keyword=0.125
```

## Test

Non-interactive, exits non-zero on failure:

```bash
python3 projects/vector-search-lab/test_app.py
```

The suite asserts: nearest-neighbour ordering is sensible, the metadata filter
excludes other categories, `delete` removes a document from both the store and
search results, and switching the hybrid blend weight changes the ranking
(including a dense-vs-keyword rank-1 inversion).

## The two Definition-of-Done queries

- **insert/load query**: `build_sample_store()` upserts the sample corpus, then
  `store.get("doc-5")` loads a document back by id.
- **read/search query**: `store.search("programming language", k=2,
  metadata_filter=has_category("tech"), hybrid_alpha=0.5)` runs a hybrid,
  metadata-filtered nearest-neighbour search.

## API surface

| Method | What it does | Vector-DB analogue |
| --- | --- | --- |
| `upsert(id, text, metadata)` | insert or overwrite by id, re-embedding the text | `table.merge_insert` (LanceDB) / `collection.upsert` (Chroma) |
| `delete(id)` | remove a document by id | `table.delete("id = ...")` / `collection.delete(ids=[...])` |
| `search(query, k, metadata_filter, hybrid_alpha)` | top-k by cosine, optional pre-filter and hybrid blend | `table.search(vec).where(...).limit(k)` / `collection.query(..., where=...)` |

`hybrid_alpha` controls the blend: `1.0` = pure dense vector search,
`0.0` = pure keyword search, in between = hybrid.

## What a vector DB is good for

- semantic / similarity retrieval where exact keywords are not enough
- RAG: fetch the most relevant chunks to ground an LLM answer
- recommendations and near-duplicate detection over embeddings
- metadata-filtered similarity (e.g. "similar docs, but only in this tenant")

## What a vector DB is NOT good for

- exact/transactional lookups by primary key — use a relational/KV store
- strong consistency, joins, and multi-row transactions
- analytical aggregations over columns — use DuckDB or a warehouse
- the source of truth for your data — keep the canonical text elsewhere and
  treat the vector index as a derived, rebuildable artifact
- precise keyword/boolean queries — that is a full-text engine's job (hybrid
  search exists precisely because dense vectors blur exact terms)

## Upgrade path

This lab teaches the API and the concepts; production uses a real embedded
vector DB and real embeddings. The shapes map directly.

### Real embeddings

Replace `embed(text)` with a call to an embedding model. The store does not
care where the vector comes from — only that every document and the query use
the **same model and dimension**:

```python
# toy (this lab):            vector = embed(text)            # dim = 64
# real (sentence-transformers): vector = model.encode(text)  # e.g. dim = 384
# real (hosted API):           vector = client.embeddings(text).data[0].embedding
```

### Swap in LanceDB (`pip install lancedb`)

```python
import lancedb
db = lancedb.connect("/tmp/lance-data")            # embedded, file-backed
table = db.create_table("docs", data=[
    {"id": "doc-1", "text": "...", "vector": embed("..."), "category": "tech"},
])
# upsert  -> merge_insert on the id column
table.merge_insert("id").when_matched_update_all().when_not_matched_insert_all().execute(rows)
# delete  -> SQL-ish predicate
table.delete("id = 'doc-1'")
# search  -> vector search + metadata filter + limit (k)
hits = table.search(embed("programming language")).where("category = 'tech'").limit(2).to_list()
# hybrid  -> create_fts_index(...) then search(query_type="hybrid")
```

### Swap in Chroma (`pip install chromadb`)

```python
import chromadb
client = chromadb.PersistentClient(path="/tmp/chroma-data")   # local, embedded
collection = client.create_collection("docs")                 # default embedder, or pass your own
collection.upsert(ids=["doc-1"], documents=["..."], metadatas=[{"category": "tech"}])
collection.delete(ids=["doc-1"])
results = collection.query(
    query_texts=["programming language"],
    n_results=2,
    where={"category": "tech"},          # metadata filter
)
```

The mental model is identical: a collection keyed by id, upsert/delete by id,
and a top-k search with a metadata filter. The differences a real DB adds are
approximate-nearest-neighbour indexing (HNSW / IVF) so search stays sub-linear
at scale, persistence, and a production-grade lexical scorer (BM25) for the
keyword half of hybrid search. This lab does an exact linear scan and a tiny
Jaccard keyword score on purpose, so the algorithm is fully visible.

## Exercises

1. **Approximate nearest neighbour.** The current `search` is an exact O(n)
   scan. Implement a crude inverted index keyed by hashed bucket so that a query
   only scores documents sharing at least one non-zero bucket, and measure how
   often it returns the same top-k as the exact scan. This is a hand-rolled
   intuition for why real vector DBs use HNSW/IVF.
2. **Chunking and document IDs.** Extend `upsert` to split a long document into
   overlapping chunks with ids like `doc-1#0`, `doc-1#1`, store each chunk
   separately, and have `delete("doc-1")` remove all of its chunks. This mirrors
   how RAG pipelines actually store documents.
3. **Tune the hybrid blend.** Add an evaluation harness with a few labelled
   (query -> relevant ids) pairs and sweep `hybrid_alpha` from 0.0 to 1.0 to
   find the value that maximizes a metric like recall@k. Note which queries
   prefer dense vs keyword.
4. **Better lexical score.** Replace `keyword_overlap` (Jaccard) with a TF-IDF
   or BM25 score computed over the corpus. Re-run exercise 3 and compare.
5. **Persistence and reload.** Serialize the store to a JSON or sqlite file
   (vectors + text + metadata) and add `load()` / `save()`. Confirm search
   results are identical before and after a round-trip — the property that makes
   a vector index a rebuildable, derived artifact.
