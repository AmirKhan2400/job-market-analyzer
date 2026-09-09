from statistics import mean, median


def aggregate_latency(latencies_ms: list[float]) -> dict[str, float | None]:
    if not latencies_ms:
        return {
            "mean_latency_ms": None,
            "median_latency_ms": None,
            "p95_latency_ms": None,
            "min_latency_ms": None,
            "max_latency_ms": None,
        }

    sorted_values = sorted(latencies_ms)

    return {
        "mean_latency_ms": mean(sorted_values),
        "median_latency_ms": median(sorted_values),
        "p95_latency_ms": percentile(sorted_values, 95),
        "min_latency_ms": min(sorted_values),
        "max_latency_ms": max(sorted_values),
    }


def percentile(sorted_values: list[float], percentile_value: float) -> float:
    if not sorted_values:
        raise ValueError("Cannot calculate percentile for an empty list.")

    if len(sorted_values) == 1:
        return sorted_values[0]

    rank = (percentile_value / 100) * (len(sorted_values) - 1)
    lower_index = int(rank)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    fraction = rank - lower_index

    return sorted_values[lower_index] + (
        sorted_values[upper_index] - sorted_values[lower_index]
    ) * fraction
