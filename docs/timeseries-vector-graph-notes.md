# Time-Series, Vector, and Graph Notes

Last verified: 2026-06-20

## Time-Series

Start with the shape of the data:

- timestamp
- entity or source
- measured fields
- tags/dimensions
- retention expectations
- query patterns

Use DuckDB to learn the shape quickly. Use InfluxDB 3 Core when the lesson needs real ingest behavior, line protocol, caches, or time-series-specific operations.

## Vector

Start with retrieval semantics:

- document ID
- chunk ID
- embedding model
- vector dimension
- metadata filters
- update/delete behavior
- hybrid search needs

Use LanceDB when an embedded local vector store is enough. Use Chroma when the lesson is closer to RAG application flow and collections.

## Graph

Start with the question:

- Do queries need multi-hop traversal?
- Are relationships first-class domain facts?
- Are path queries central?
- Does the graph need algorithms or visualization?

Use Kuzu to learn embedded property graph modeling. Use Neo4j when the lesson needs the fuller Cypher ecosystem, vector indexes, visualization, or graph data science.

## Maintenance Notes

- Kuzu is useful as an embedded graph learning tool, but the original `kuzudb/kuzu` repository was archived in October 2025. Use it intentionally and document that risk.
- Neo4j is current and has a broader ecosystem, but it is not a no-Docker embedded database in the same way as H2, DuckDB, or LanceDB.
