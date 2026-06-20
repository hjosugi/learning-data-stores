# Multimodel DB Lab

Compare time-series, vector-search, and graph-query ideas with only Python and SQLite.

This is not a replacement for InfluxDB, LanceDB, Chroma, Kuzu, or Neo4j. It is a small
lab for learning the data shape before adding a specialized database.

## Run

```bash
python3 projects/multimodel-db-lab/app.py
python3 projects/multimodel-db-lab/test_app.py
```

## What To Notice

- Time-series data needs a timestamp, a retention/export story, and bucketed reads.
- Vector search needs an embedding model, a similarity metric, and an index once data grows.
- Graph queries need explicit relationships and traversal rules.
- SQLite can model all three for learning, but specialized databases matter when ingest,
  indexing, query language, or operations become the point of the exercise.
