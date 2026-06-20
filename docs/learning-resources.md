# Further learning resources

Curated primary sources for this repo's named technologies, with an emphasis on
the vector-database track (embedding storage, dense/cosine search, metadata
filtering, hybrid search, upsert/delete). Prefer these canonical roots over
guessed deep links.

Last verified: 2026-06-21

## Vector databases (LanceDB, Chroma)

- **LanceDB documentation** — https://docs.lancedb.com/
  Official docs for the embedded, file-backed vector database. Covers tables,
  vector + scalar (metadata) search, `merge_insert` upsert, delete, full-text
  and hybrid search, and ANN indexing. This is the closest real tool to this
  lab's `VectorStore`.

- **Chroma documentation** — https://docs.trychroma.com/
  Official docs for Chroma collections. Shows `add` / `upsert` / `delete` by id,
  `query` with `where` metadata filters, and how a default embedding function is
  applied — the API this lab deliberately mirrors.

- **Lance / Lance format (GitHub)** — https://github.com/lancedb/lance
  The columnar storage format underneath LanceDB. Useful for understanding how a
  vector index is persisted as a derived, rebuildable artifact rather than a
  source of truth.

## Embeddings and similarity (the "vector" in vector DB)

- **Sentence-Transformers documentation** — https://www.sbert.net/
  The canonical open-source library for producing real text embeddings. Read
  this to replace the toy `embed()` with a model that captures meaning, and to
  understand embedding dimension and normalization.

- **OpenAI embeddings guide** — https://platform.openai.com/docs/guides/embeddings
  Vendor reference for hosted embeddings: model choice, dimensions, and cosine
  similarity for search/clustering. A drop-in source of production vectors.

- **Cloudflare Vectorize / Workers AI docs** — https://developers.cloudflare.com/vectorize/
  A managed vector index with metadata filtering and Workers AI embeddings.
  Shows the same upsert/query/filter model in a serverless context.

## Search foundations (the lexical half of hybrid search)

- **SQLite FTS5 documentation** — https://sqlite.org/fts5.html
  Full-text search inside an embedded database, including BM25 ranking. The
  realistic upgrade for this lab's tiny Jaccard `keyword_overlap`, and the basis
  of the repo's planned `search-sqlite-fts` example.

- **Introduction to Information Retrieval (Manning, Raghavan, Schütze)** —
  https://nlp.stanford.edu/IR-book/
  The standard free textbook. Chapters on the vector space model, cosine
  similarity, TF-IDF, and evaluation (precision/recall@k) explain *why* the
  scoring in this lab works and how to measure retrieval quality.

## The rest of the repo's named stores

- **DuckDB documentation** — https://duckdb.org/docs/current/
  Embedded analytical SQL; the right tool when the task is aggregation rather
  than similarity (see the "not good for" section of the vector lab).

- **InfluxDB 3 Core documentation** — https://docs.influxdata.com/influxdb3/core/
  Time-series ingest and query behavior for the time-series track.

- **Neo4j documentation** — https://neo4j.com/docs/
  Property-graph modeling, Cypher, and vector indexes inside a graph database.

- **Kuzu (GitHub)** — https://github.com/kuzudb/kuzu
  Embedded property-graph engine for Cypher experiments (note the archival
  maintenance warning in `docs/timeseries-vector-graph-notes.md`).

- **H2 Database** — https://www.h2database.com/html/main.html
  Embedded relational database for the Java/JDBC fixture track.
