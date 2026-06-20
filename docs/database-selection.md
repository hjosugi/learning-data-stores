# Database Selection Notes

Last verified: 2026-06-20

## Selection Matrix

| Need | Start with | Upgrade to | Why |
| --- | --- | --- | --- |
| Java integration tests | H2 | PostgreSQL/Testcontainers | Fast feedback first, real dialect later |
| local analytics | DuckDB | data warehouse/lakehouse | DuckDB is embedded and file-friendly |
| simple time-series analysis | DuckDB | InfluxDB 3 Core | Start with SQL files, then test real ingest/cache behavior |
| AI retrieval prototype | LanceDB | LanceDB Enterprise or another managed vector DB | Embedded local vector search is enough for learning |
| local RAG collection | Chroma | Chroma Cloud/self-hosted server | Easy local retrieval model |
| graph data modeling | Kuzu | Neo4j | Kuzu is embedded; Neo4j is the fuller graph ecosystem |
| graph algorithms / graph platform | Neo4j | Neo4j Aura or managed deployment | Tooling, Cypher docs, vector indexes, graph data science |

## Rule of Thumb

- Use embedded databases to learn modeling and query shape.
- Use server databases to learn operations, network behavior, auth, indexes, backups, and production tradeoffs.
- Do not use H2 as proof that PostgreSQL/MySQL behavior is correct.
- Do not use DuckDB as an OLTP application database.
- Do not use a vector DB before writing down the document ID, chunking, metadata, and update strategy.
- Do not use a graph DB just because data has relationships; use it when relationship traversal is the central query.

## Dockerless Priority

1. Prefer embedded libraries.
2. Prefer local single binary/process.
3. Use Docker only when the real system behavior matters and no embedded mode is honest.
