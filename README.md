# Learning Data Stores

Relational, analytical, time-series, vector, graph, and embedded database experiments for learning.

Last verified: 2026-06-20

## Why This Repo Exists

Application repos should not become database catalogs. This repo keeps database experiments small, comparable, and runnable.

The rule is:

- prefer no-Docker embedded examples first
- use local files and generated sample data
- add server databases only when their real behavior matters
- document when a lightweight substitute is acceptable and when it is misleading

## Learning Path

1. SQL basics with H2 and SQLite-style embedded databases
2. Analytical SQL with DuckDB
3. Time-series modeling with DuckDB first, then InfluxDB 3 Core
4. Vector search with LanceDB and Chroma
5. Graph modeling with Kuzu first, then Neo4j
6. Search and hybrid retrieval
7. Choosing the right database for an app
8. Backup, migration, indexing, and operational tradeoffs

## Planned Structure

```text
examples/
  relational-h2/
  analytics-duckdb/
  timeseries-duckdb/
  timeseries-influxdb3/
  vector-lancedb/
  vector-chroma/
  graph-kuzu/
  graph-neo4j/
  search-sqlite-fts/
docs/
  2026-learning-items.md
  database-selection.md
  dockerless-strategy.md
  repository-profile.md
  timeseries-vector-graph-notes.md
```

## Dockerless First

Good default experiments:

- H2 for embedded relational Java tests
- DuckDB for local analytical SQL and time-series-shaped data
- LanceDB for embedded vector search
- Chroma for local vector retrieval experiments
- Kuzu for embedded graph/Cypher experiments, with a maintenance warning

Optional server experiments:

- InfluxDB 3 Core for real time-series ingest/query behavior
- Neo4j for production-style graph database behavior, Cypher tooling, vector indexes, and graph data science

## References

- DuckDB documentation: https://duckdb.org/docs/current/
- InfluxDB 3 Core documentation: https://docs.influxdata.com/influxdb3/core/
- LanceDB documentation: https://docs.lancedb.com/
- Chroma documentation: https://docs.trychroma.com/
- Neo4j documentation: https://neo4j.com/docs/
- Kuzu repository: https://github.com/kuzudb/kuzu
- H2 Database: https://www.h2database.com/html/main.html
