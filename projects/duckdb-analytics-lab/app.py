from __future__ import annotations

import duckdb


def run_query() -> list[tuple[str, float]]:
    connection = duckdb.connect(":memory:")
    connection.sql(
        """
        create table events(service varchar, latency_ms integer);
        insert into events values
          ('api', 120), ('api', 180), ('api', 90),
          ('worker', 240), ('worker', 210);
        """
    )
    return connection.sql(
        """
        select service, round(avg(latency_ms), 2) as avg_latency_ms
        from events
        group by service
        order by service
        """
    ).fetchall()


def main() -> None:
    for service, avg_latency in run_query():
        print(f"{service}: {avg_latency}ms")


if __name__ == "__main__":
    main()

