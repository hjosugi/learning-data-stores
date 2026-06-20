# 2026 Learning Items: Data Stores

Last verified: 2026-06-20

## Must Learn

### Embedded relational databases

- H2 embedded mode
- in-memory vs file-backed data
- schema migration basics
- constraints and transactions
- test fixture design

Projects:

- `examples/relational-h2`: small Java/JDBC or Spring test fixture

### Analytical SQL

- DuckDB local database files
- CSV/JSON/Parquet import
- aggregation and window functions
- time bucketing with SQL
- query plans and profiling

Projects:

- `examples/analytics-duckdb`: local analytics notebook or CLI
- `examples/timeseries-duckdb`: time-series-shaped data without a server

### Time-series databases

- measurement/table design
- timestamp precision
- tags vs fields
- retention
- last-value and distinct-value caches
- SQL vs InfluxQL boundaries

Projects:

- `examples/timeseries-influxdb3`: InfluxDB 3 Core local process example

### Vector databases

- embedding storage
- metadata filtering
- dense vector search
- full-text and hybrid search
- chunking and document IDs
- update/delete semantics

Projects:

- `examples/vector-lancedb`: embedded vector search
- `examples/vector-chroma`: local retrieval collection

### Graph databases

- property graph modeling
- nodes, relationships, labels, properties
- Cypher basics
- path queries
- graph vs relational tradeoffs
- vector indexes in graph workflows

Projects:

- `examples/graph-kuzu`: embedded Cypher experiment
- `examples/graph-neo4j`: optional Neo4j server example

## Definition of Done

- Every example has generated sample data.
- Every example has a `Run` command.
- Every example has one query to insert/load and one query to read/search.
- Each database page explains what the database is good for and what it is not good for.
- Server examples include a no-Docker alternative or explicitly explain why one is not realistic.
