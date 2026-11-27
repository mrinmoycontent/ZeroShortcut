# ZeroShortcut – Visual Task Factory

ZeroShortcut is a reproducible prototype for generating synthetic visual chart tasks, validating their reference answers, evaluating a vision-language model, and analysing model errors. The packaged release contains a V2 dataset of 24 chart images and 144 questions.

## Verified project results

- **24** synthetic chart tasks across four chart families: vertical bar, horizontal bar, line, and lollipop.
- **144** questions across seven question types.
- **24/24** packaged tasks pass reference-answer and image validation.
- **4/4** adversarial fault-injection scenarios are detected.
- **NVIDIA Nemotron 3.5 Super VL** was evaluated on all 24 charts / 144 questions through OpenRouter.
- **119/144 correct; 25/144 incorrect; 82.64% accuracy** under exact numeric and normalized text scoring.
- A second-model comparison has not yet been completed.

The reported 82.64% is specific to this synthetic 24-chart dataset and the recorded model/configuration. It should not be interpreted as a general measure of visual reasoning ability.

## Benchmark findings

| Chart family | Correct | Questions | Accuracy |
|---|---:|---:|---:|
| Vertical bar | 31 | 36 | 86.11% |
| Horizontal bar | 32 | 36 | 88.89% |
| Line | 27 | 36 | 75.00% |
| Lollipop | 29 | 36 | 80.56% |

| Question type | Correct | Questions | Accuracy |
|---|---:|---:|---:|
| Highest category | 24 | 24 | 100.00% |
| Second highest | 24 | 24 | 100.00% |
| Value lookup | 24 | 24 | 100.00% |
| Absolute difference | 18 | 24 | 75.00% |
| Count above threshold | 10 | 24 | 41.67% |
| Total value | 16 | 18 | 88.89% |
| Largest step change | 3 | 6 | 50.00% |

In this run, the weakest chart family was line charts (75.00%), and the weakest question type was count-above-threshold (41.67%). These are observations about this benchmark run, not broad generalisation claims.

## Repository layout

```text
ZeroShortcut/
├── data/
│   ├── visual_tasks_v2.json
│   └── images_v2/                  # 24 chart PNGs
├── evaluations/nemotron/          # raw responses and scored task records
├── reports/                       # validation and benchmark reports
├── evidence/screenshots/          # Colab output screenshots
├── zeroshortcut/                   # shared validation logic
├── tests/                          # pytest tests
├── notebooks/ZeroShortcut_Visual_Task_Factory.ipynb
├── generate.py
├── validate.py
├── adversarial_test.py
├── create_report.py
├── evaluate_openrouter.py
├── requirements.txt
└── README.md
```

## Run locally or in Google Colab

Use Python 3.10 or later. From this repository root:

```bash
python -m pip install -r requirements.txt
python validate.py
python adversarial_test.py
python create_report.py
python -m pytest -q
```

The packaged dataset, generated images, evaluation evidence, and benchmark reports are included. The commands validate the existing data and regenerate summary reports.

### Regenerate the dataset

```bash
python generate.py --output-dir data --count 24 --seed 20261123
python validate.py
python adversarial_test.py
python create_report.py
```

The line-chart generator resamples values until the largest consecutive absolute change is unique, preventing an ambiguous `largest_step_change` reference answer. Regeneration overwrites the packaged JSON and PNGs; keep a backup before changing the seed or task count.

### Re-run external model evaluation

The project includes `evaluate_openrouter.py`, which uses the OpenRouter chat-completions endpoint and the model `nvidia/nemotron-3.5-super-vl:free`. Set `OPENROUTER_API_KEY` as an environment variable; never hard-code or commit API keys. The evaluator saves raw responses and scored files per task and skips tasks that already have six saved answers. Read `evaluations/README.md` before running it. Free model availability and quotas can change.

Example:

```bash
export OPENROUTER_API_KEY="your-key"
python evaluate_openrouter.py --resume
```

## Validation approach

The validator recomputes answers from each task's structured source data, checks task/question identifiers, resolves image paths relative to the dataset, and verifies the PNG files. The adversarial suite mutates in-memory copies to test incorrect reference answers, missing image files, duplicate task IDs, and tied values.

## Evidence and limitations

- `reports/nemotron_final_benchmark.json` contains the final 144-answer model evaluation and breakdowns.
- `reports/nemotron_detailed_results.csv` contains per-question scoring.
- `evaluations/nemotron/` contains raw model responses and per-task scoring records. An initial failed ZS2_001 attempt is retained as `ZS2_001_initial_failed_attempt.json`; the successful retry is the raw `ZS2_001.json` and the scored result is `ZS2_001_scored.json`.
- `evidence/screenshots/` contains two screenshots of the generated chart gallery.
- The benchmark covers only synthetic business charts, one model, 24 images and 144 questions. No second-model comparison or broad external generalisation study has been completed.

## Technical explanation and validation log

See [TECHNICAL_EXPLANATION.md](TECHNICAL_EXPLANATION.md) for the Track 2 problem definition, practical impact, architecture, design decisions, assumptions, model findings, and limitations. The recorded final checks are in `evidence/validation_test_run.log`.
