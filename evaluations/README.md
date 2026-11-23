# External model evaluation

The packaged benchmark already contains all 24 raw Nemotron responses and all 24 scored task records. No API call is needed to inspect the included results.

## Re-run the benchmark

1. Create an OpenRouter API key and make sure the chosen model endpoint is available on your account. Free model availability and quotas can change.
2. Set the key in your shell or notebook environment as `OPENROUTER_API_KEY`. Do not paste the key into a source file or commit it.
3. Install requirements with `python -m pip install -r requirements.txt`.
4. Run `python evaluate_openrouter.py --resume`. Existing complete scored task files are skipped.

To evaluate a single task, run `python evaluate_openrouter.py --task-id ZS2_001`.

The evaluator requests one JSON answer per question, saves raw API responses and writes scored records. It uses exact numeric matching and normalized text matching. Review the scoring methodology and limitations in `reports/nemotron_final_benchmark.md`.
