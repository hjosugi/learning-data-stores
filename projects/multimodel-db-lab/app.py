from __future__ import annotations

import json
import math
import sqlite3
from collections import deque
from pathlib import Path
from typing import Iterable


def connect(path: str | Path = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        create table if not exists sensor_events (
          device_id text not null,
          ts integer not null,
          value real not null,
          primary key (device_id, ts)
        );

        create table if not exists documents (
          id text primary key,
          title text not null,
          embedding text not null
        );

        create table if not exists graph_edges (
          src text not null,
          dst text not null,
          primary key (src, dst)
        );

        create index if not exists idx_sensor_events_ts on sensor_events(ts);
        """
    )
    return conn


def seed(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        delete from sensor_events;
        delete from documents;
        delete from graph_edges;
        """
    )
    conn.executemany(
        "insert into sensor_events(device_id, ts, value) values (?, ?, ?)",
        [
            ("sensor-a", 0, 19.8),
            ("sensor-a", 30, 20.2),
            ("sensor-a", 60, 21.0),
            ("sensor-a", 90, 22.0),
            ("sensor-b", 0, 18.5),
            ("sensor-b", 60, 18.9),
        ],
    )
    conn.executemany(
        "insert into documents(id, title, embedding) values (?, ?, ?)",
        [
            ("d1", "time-series ingest", json.dumps([0.9, 0.1, 0.0])),
            ("d2", "vector search basics", json.dumps([0.1, 0.95, 0.1])),
            ("d3", "graph traversal", json.dumps([0.0, 0.2, 0.9])),
        ],
    )
    conn.executemany(
        "insert into graph_edges(src, dst) values (?, ?)",
        [
            ("browser", "api"),
            ("api", "database"),
            ("api", "queue"),
            ("queue", "worker"),
            ("worker", "database"),
        ],
    )
    conn.commit()


def bucket_averages(conn: sqlite3.Connection, bucket_seconds: int) -> list[dict[str, float]]:
    rows = conn.execute(
        """
        select
          (ts / ?) * ? as bucket_start,
          round(avg(value), 2) as avg_value,
          count(*) as samples
        from sensor_events
        group by bucket_start
        order by bucket_start
        """,
        (bucket_seconds, bucket_seconds),
    ).fetchall()
    return [dict(row) for row in rows]


def cosine_similarity(left: Iterable[float], right: Iterable[float]) -> float:
    left_values = list(left)
    right_values = list(right)
    dot = sum(a * b for a, b in zip(left_values, right_values))
    left_norm = math.sqrt(sum(a * a for a in left_values))
    right_norm = math.sqrt(sum(b * b for b in right_values))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def nearest_documents(
    conn: sqlite3.Connection, query_embedding: list[float], limit: int = 2
) -> list[dict[str, float | str]]:
    rows = conn.execute("select id, title, embedding from documents").fetchall()
    scored = []
    for row in rows:
        score = cosine_similarity(json.loads(row["embedding"]), query_embedding)
        scored.append({"id": row["id"], "title": row["title"], "score": round(score, 4)})
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]


def shortest_path(conn: sqlite3.Connection, src: str, dst: str) -> list[str] | None:
    adjacency: dict[str, list[str]] = {}
    for row in conn.execute("select src, dst from graph_edges"):
        adjacency.setdefault(row["src"], []).append(row["dst"])

    queue: deque[list[str]] = deque([[src]])
    seen = {src}
    while queue:
        path = queue.popleft()
        current = path[-1]
        if current == dst:
            return path
        for next_node in adjacency.get(current, []):
            if next_node not in seen:
                seen.add(next_node)
                queue.append([*path, next_node])
    return None


def demo() -> dict[str, object]:
    conn = connect()
    seed(conn)
    return {
        "timeseries": bucket_averages(conn, bucket_seconds=60),
        "vector": nearest_documents(conn, [0.05, 0.95, 0.05]),
        "graph": shortest_path(conn, "browser", "database"),
    }


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2))
