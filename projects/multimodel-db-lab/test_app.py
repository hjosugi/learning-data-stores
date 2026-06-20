from app import (
    bucket_averages,
    connect,
    nearest_documents,
    seed,
    shortest_path,
)


def main() -> None:
    conn = connect()
    seed(conn)

    buckets = bucket_averages(conn, bucket_seconds=60)
    assert buckets == [
        {"bucket_start": 0, "avg_value": 19.5, "samples": 3},
        {"bucket_start": 60, "avg_value": 20.63, "samples": 3},
    ]

    nearest = nearest_documents(conn, [0.05, 0.95, 0.05], limit=1)
    assert nearest[0]["id"] == "d2"
    assert nearest[0]["score"] > 0.99

    assert shortest_path(conn, "browser", "database") == ["browser", "api", "database"]
    assert shortest_path(conn, "queue", "browser") is None
    print("ok")


if __name__ == "__main__":
    main()
