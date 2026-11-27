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

## Technical Explanation

### Problem Definition and Practical Impact

ZeroShortcut is a Track 2 Visual Problem and Model Evaluation project. It evaluates how well vision-language models understand synthetic business charts and answer questions involving rankings, numerical values, comparisons, totals, thresholds, and changes over time.

Business reports frequently use charts to communicate operational performance. Incorrectly reading chart values or trends can lead to misleading interpretations. ZeroShortcut provides a repeatable way to generate chart-based reasoning tasks and measure model performance against independently calculated reference answers.

### Pipeline Architecture

The pipeline consists of five stages:

1. **Task Generation:** `generate.py` creates synthetic business data, chart images, questions, and reference answers.
2. **Chart Rendering:** Matplotlib generates four chart families: vertical bar, horizontal bar, line, and lollipop charts.
3. **Reference Validation:** `validate.py` checks task structure, expected answers, identifiers, and image files.
4. **Adversarial Validation:** `adversarial_test.py` tests whether the validator detects incorrect answers, missing images, duplicate task IDs, and ambiguous tied values.
5. **Model Evaluation and Reporting:** `evaluate_openrouter.py` evaluates chart images using NVIDIA Nemotron 3.5 Super VL. `create_report.py` generates consolidated reports.

### Dataset and Task Variation

The V2 dataset contains 24 charts and 144 questions, with six charts per chart family.

Seven question types are included:

- Highest category
- Second-highest category
- Value lookup
- Absolute difference
- Count above threshold
- Total value
- Largest step change

Variation is introduced through chart families, synthetic values, business categories, monthly periods, metrics, and question types.

### Design Decisions and Assumptions

- Synthetic data is used so reference answers can be calculated independently.
- Each generated chart is associated with structured source data and reference answers.
- Line-chart generation avoids tied largest consecutive changes to prevent ambiguous answers.
- The evaluated model receives chart images and questions, not the underlying reference answers.
- Numerical answers are evaluated using exact numeric comparison, while text answers use normalization.
- The benchmark is limited to synthetic business charts and is not intended to represent every real-world chart or visual reasoning scenario.

### Model Selection

NVIDIA Nemotron 3.5 Super VL was selected for image-based visual question answering through OpenRouter.

The model was evaluated on all 24 charts and 144 questions.

Results:

- Correct answers: 119
- Incorrect answers: 25
- Accuracy: 82.64%

The results are specific to this dataset, model, and evaluation configuration. A second-model comparison has not been completed.

### Validation Results

- Dataset validation: 24 out of 24 tasks passed.
- Adversarial validation: 4 out of 4 fault scenarios detected.
- Automated pipeline tests: 8 tests passed.

### Limitations and Future Work

The current benchmark uses a limited synthetic dataset and one external model. Future improvements could include more chart families, larger datasets, additional vision-language models, and carefully verified real-world business charts.
