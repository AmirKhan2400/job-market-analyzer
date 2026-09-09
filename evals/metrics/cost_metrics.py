def estimate_cost(
    input_tokens: int | None,
    output_tokens: int | None,
    input_per_million: float | None,
    output_per_million: float | None,
) -> float | None:
    if (
        input_tokens is None
        or output_tokens is None
        or input_per_million is None
        or output_per_million is None
    ):
        return None

    return (input_tokens / 1_000_000 * input_per_million) + (
        output_tokens / 1_000_000 * output_per_million
    )
