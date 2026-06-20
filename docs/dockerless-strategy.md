# Dockerless Strategy

Last verified: 2026-06-20

## Goal

Make most database lessons runnable without Docker.

Docker is useful, but it should not be the only way to learn a database concept. The first lesson for each database should run on a normal developer machine with language package managers or a local binary.

## Good Dockerless Fits

| Database | Dockerless approach |
| --- | --- |
| H2 | Java dependency, in-memory or file-backed |
| DuckDB | CLI, Python package, Node package, or JDBC |
| LanceDB | Python or TypeScript embedded library |
| Chroma | local SDK/client or local server command |
| Kuzu | embedded library, with maintenance warning |

## Server-Oriented Fits

| Database | Dockerless approach | Note |
| --- | --- | --- |
| InfluxDB 3 Core | local `influxdb3 serve` process | Real behavior needs a running server |
| Neo4j | local install, Desktop, Aura, or optional Docker | Embedded substitute does not teach full Neo4j operations |

## Lesson Requirements

Each lesson should say:

- whether Docker is required
- how data is stored on disk
- how to delete local data safely
- how to regenerate sample data
- what would change in a production deployment
