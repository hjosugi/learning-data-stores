from __future__ import annotations

import sqlite3


def setup(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        create table task(id integer primary key, title text not null, status text not null);
        create table event(ts integer not null, name text not null, value real not null);
        create table edge(source text not null, target text not null);
        insert into task(title, status) values
          ('compare embedded databases', 'open'),
          ('write query notes', 'done');
        insert into event(ts, name, value) values
          (1, 'cpu', 0.30), (2, 'cpu', 0.65), (3, 'cpu', 0.40),
          (1, 'mem', 0.50), (2, 'mem', 0.70);
        insert into edge(source, target) values
          ('api', 'service'), ('service', 'database'), ('service', 'queue');
        """
    )


def main() -> None:
    with sqlite3.connect(":memory:") as connection:
        setup(connection)
        open_tasks = connection.execute("select title from task where status = 'open'").fetchall()
        cpu_average = connection.execute("select avg(value) from event where name = 'cpu'").fetchone()[0]
        service_edges = connection.execute("select target from edge where source = 'service'").fetchall()

    print("open_tasks=", [row[0] for row in open_tasks])
    print("cpu_average=", round(cpu_average, 3))
    print("service_edges=", [row[0] for row in service_edges])


if __name__ == "__main__":
    main()

