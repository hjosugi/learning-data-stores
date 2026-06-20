from app import run_workload


def test_workload_queries() -> None:
    result = run_workload()
    assert result["open_tasks"] == ["compare embedded databases"]
    assert result["cpu_average"] == 0.45
    assert result["service_edges"] == ["database", "queue"]


if __name__ == "__main__":
    test_workload_queries()
    print("ok")

