# LLM Evaluation Subsystem

This folder contains a standalone evaluation and benchmarking subsystem for AI Job Market Analyzer.

It is intentionally separate from the production FastAPI app. Production code should not import from `evals/`, and eval code should not add routes, database tables, or application startup behavior.

## Why This Exists

The application has two different LLM workloads:

1. Job extraction: raw job description to structured `JobOffer`
2. Recommendation generation: match information to a concise recommendation

These need separate evaluation because extraction is mostly structured correctness, while recommendations require human judgment.

The practical engineering question is not:

> Which model is globally best?

The better question is:

> Which model provides sufficient quality for this specific workload at acceptable cost, latency, and reliability?

Quality, cost, latency, and reliability are competing production concerns. A model can be highly accurate but too slow, cheap but unreliable, or fast but weak at structured output.

## Model Benchmarking vs Production Routing

Production uses dashboard-managed routing:

- Requesty Fallback Policies
- OpenRouter Presets

Benchmarks in this folder target individual model IDs directly. That lets you learn which model actually produced each response.

After comparing individual models, use the results to design or update your Requesty/OpenRouter dashboard policies. Do not benchmark a preset or policy when your goal is to compare individual models.

## Configuration

Edit:

```text
evals/config.yaml
```

Model entries look like:

```yaml
models:
  - name: gemini-flash
    provider: openrouter
    model: google/gemini-2.5-flash
    enabled: true
    max_tokens: 1200
    reasoning_enabled: false
    require_parameters: true
    input_per_million:
    output_per_million:
```

Set `enabled: false` to keep a model in the file without running it.

Each model can define an explicit output cap:

```yaml
models:
  - name: gemini-flash
    provider: openrouter
    model: google/gemini-2.5-flash
    enabled: true
    max_tokens: 1200
    reasoning_enabled: false
    require_parameters: true
```

Extraction and recommendation requests also define fallback output caps:

```yaml
extraction:
  max_tokens: 1200

recommendation:
  max_tokens: 300
```

This is important for OpenRouter. Without an explicit output cap, some models may
reserve their full maximum context window and fail with a credit error even when
the actual answer would be small.

If a model entry has `max_tokens`, that value is used. If it is blank or missing,
the extraction or recommendation fallback value is used.

OpenRouter reasoning can also be controlled per model:

```yaml
reasoning_enabled: false
```

Keep it disabled for structured extraction unless you intentionally want to
benchmark reasoning behavior and cost.

OpenRouter structured-output provider filtering is controlled per model:

```yaml
require_parameters: true
```

When true, OpenRouter only routes to endpoints that support the requested
parameters, such as JSON schema response formatting. When false, OpenRouter may
route to endpoints that ignore unsupported parameters, which can be useful for
debugging but makes structured extraction less reliable.

API keys are read from environment variables:

```env
OPENROUTER_API_KEY=...
REQUESTY_API_KEY=...
```

Never put API keys in `config.yaml`, datasets, result files, or logs.

## Pricing

Pricing is configured inside each model entry in `evals/config.yaml`:

```yaml
models:
  - name: gemini-flash
    provider: openrouter
    model: google/gemini-2.5-flash
    enabled: true
    input_per_million:
    output_per_million:
```

Fill the rates before a real run. Vendor pricing changes, so keep these values current. If pricing or token usage is unavailable, cost is stored as empty instead of guessed.

Cost is calculated as:

```text
input_tokens / 1,000,000 * input_rate
+
output_tokens / 1,000,000 * output_rate
```

## Ground Truth

Extraction cases live in:

```text
evals/datasets/extraction_cases.json
```

The included cases are examples only. Useful benchmarks require manually reviewed ground truth from real job descriptions.

Do not fabricate many fake cases just to make charts look impressive. A small, accurate dataset is more valuable than a large noisy one.

## Extraction Metrics

Extraction uses production parity:

- Same `JobOffer` schema
- Same extraction prompt
- Same strict JSON Schema response format
- `description` removed from generated schema
- Original description restored after validation

Extraction quality is measured only on `required_skills` and `preferred_skills`.
Other `JobOffer` fields can still appear in raw predictions for debugging, but they do
not affect model selection.

Skill comparisons use simple normalization:

- trim whitespace
- case-insensitive comparison

They do not use fuzzy matching, embeddings, or aggressive semantic normalization,
because that can hide model mistakes.

Both required and preferred skills use set-based precision, recall, and F1:

- Precision: of the skills the model predicted, how many were correct?
- Recall: of the expected skills, how many did the model find?
- F1: balance between precision and recall

Extra skills and missing skills are counted separately for required and preferred
skills. Extra skills are a useful hallucination signal, but they are not a perfect
hallucination measurement.

Reports also include `combined_skills_f1`, calculated by default as:

```text
required_skills_f1 * 0.75 + preferred_skills_f1 * 0.25
```

The weights are configurable in `evals/config.yaml`. Required skills carry more
weight because they matter more for matching and recommendations. The combined
score exists for charts and threshold comparisons; it does not replace the
individual required/preferred metrics.

## Recommendation Evaluation

Recommendations are subjective, so the subsystem does not use exact-match accuracy.

Generated recommendations are saved to:

```text
recommendation_human_review.csv
```

Fill these columns manually:

| Score | Meaning |
| --- | --- |
| 5 | Excellent |
| 4 | Good |
| 3 | Acceptable |
| 2 | Weak |
| 1 | Poor |

Rating fields:

- `relevance_score`: answers the actual role/match situation
- `faithfulness_score`: avoids inventing candidate or job facts
- `usefulness_score`: gives practical guidance
- `clarity_score`: readable and concise
- `overall_score`: overall human preference
- `notes`: reviewer comments

After entering ratings, regenerate reports:

```bash
uv run python -m evals.run report evals/results/<run-directory>
```

V1 intentionally avoids LLM-as-a-judge. That can be added later, but human scoring is easier to understand and audit.

## Latency

Latency is measured with Python's monotonic performance timer around each model request.

Reports include:

- mean latency
- median latency
- P95 latency
- minimum
- maximum

P95 matters because production users feel slow tail requests, not only averages.

## Results

Each run is saved under:

```text
evals/results/YYYY-MM-DD_HHMMSS/
```

Typical outputs:

```text
extraction_raw.csv
extraction_predictions.jsonl
extraction_summary.csv
recommendations_raw.csv
recommendation_human_review.csv
model_summary.csv
metadata.json
report.md
charts/
```

`extraction_raw.csv` includes an `llm_response` column with the complete raw
model answer for each extraction request. This makes schema failures easier to
debug without opening the JSONL predictions file.

Generated run outputs are ignored by Git by default. Keep final portfolio assets by copying selected charts into a future tracked docs/assets folder.

## Charts

Generated charts include:

- `required_skills_f1.png`
- `preferred_skills_f1.png`
- `skills_f1_comparison.png`
- `schema_valid_rate.png`
- `latency_comparison.png`
- `cost_per_request.png`
- `quality_vs_cost.png`
- `quality_vs_latency.png`
- `recommendation_quality.png`
- `model_comparison_overview.png`

Resume-friendly copies are placed in:

```text
charts/resume/
```

The overview chart normalizes:

- combined skill extraction quality
- cost efficiency
- latency efficiency

to a 0-100 scale. Cost and latency are inverted because lower is better.

## Commands

Run extraction benchmarks:

```bash
uv run python -m evals.run extraction
```

Run recommendation generation:

```bash
uv run python -m evals.run recommendation
```

Run both:

```bash
uv run python -m evals.run all
```

Regenerate report and charts after entering human ratings:

```bash
uv run python -m evals.run report evals/results/<run-directory>
```

## Adding a Model

Add another entry in `evals/config.yaml`:

```yaml
models:
  - name: my-model-name
    provider: openrouter
    model: provider/model-id
    enabled: true
    max_tokens: 1200
    reasoning_enabled: false
    require_parameters: true
    input_per_million:
    output_per_million:
```

## How Results Should Influence Routing

Use benchmark evidence to decide:

- which models belong in the Requesty policy
- which models belong in the OpenRouter preset
- which model should be first for extraction
- which models are good fallbacks
- which models are too slow or expensive for the benefit they provide

Keep the application code stable. Change model ordering in the provider dashboards when possible.
