# ZeroShortcut – Visual Task Factory

ZeroShortcut is a reproducible prototype for generating synthetic visual chart tasks, validating their reference answers, evaluating a vision-language model, and analysing model errors.

This project is submitted under **Track 2: Visual Problem & Model Evaluation** of the Innodata AI Hackathon.

## 1. Problem Definition and Practical Impact

Business decisions often depend on interpreting charts correctly. Misreading a value, comparing the wrong categories, overlooking a trend, or incorrectly counting values against a threshold can lead to inaccurate conclusions.

ZeroShortcut evaluates whether a vision-language model can interpret synthetic business charts and answer structured questions about their contents.

The project creates chart images with independently calculated reference answers. Model responses are then compared against those reference answers to identify strengths, weaknesses, and common error patterns.

## 2. Dataset and Task Scope

The V2 dataset contains:

- **24 synthetic chart images**
- **4 chart families**
- **144 questions**
- **7 question types**

The four chart families are:

1. Vertical bar charts
2. Horizontal bar charts
3. Line charts
4. Lollipop charts

The seven question types are:

1. Highest category
2. Second-highest category
3. Value lookup
4. Absolute difference
5. Count above threshold
6. Total value
7. Largest step change

The dataset uses synthetic regional, monthly, and business-metric examples. It does not represent real company data.

## 3. Pipeline Architecture

ZeroShortcut uses a five-stage pipeline.

### Stage 1: Generate Tasks and Images

**File:** `generate.py`

A reproducible random seed generates structured source data, renders chart images, assigns task IDs, and creates questions with reference answers.

### Stage 2: Validate Reference Answers and Assets

**Files:** `validate.py`, `zeroshortcut/core.py`

The validator independently recalculates expected answers from the structured data, checks task and question identifiers, resolves image paths, and verifies that the required image files exist.

### Stage 3: Adversarial Validation

**File:** `adversarial_test.py`

Controlled mutations test whether the validation pipeline detects:

- Incorrect reference answers
- Missing image files
- Duplicate task IDs
- Ambiguous tied values

### Stage 4: Vision-Language Model Evaluation

**File:** `evaluate_openrouter.py`

The chart images and associated questions are evaluated using NVIDIA Nemotron 3.5 Super VL through OpenRouter.

The model receives the chart image and questions, not the original structured source data or reference answers.

Raw model responses and scored results are saved for inspection and reproducibility.

### Stage 5: Reporting and Analysis

**File:** `create_report.py`

The reporting pipeline consolidates task counts, validation results, benchmark metrics, and evaluation findings into report files.

## 4. Design Decisions and Assumptions

- **Synthetic source data:** Structured values are retained so reference answers can be calculated independently of model responses.
- **Four chart families:** Different visual encodings are included while keeping the benchmark focused and manageable.
- **Multiple reasoning types:** Questions cover both direct chart reading and numerical reasoning, including rankings, differences, totals, threshold counts, and step changes.
- **Ambiguity prevention:** The line-chart generator resamples values until the largest consecutive absolute change is unique.
- **Image-based evaluation:** The model receives the chart image rather than the underlying source table.
- **Deterministic scoring:** Numeric answers are compared exactly. Text answers are normalised for common equivalent forms, including month abbreviations and separators.
- **Reproducibility:** The generator uses a fixed default seed, and raw model outputs, scored task files, and aggregate reports are retained.

## 5. Validation Results

The packaged V2 validation results are:

| Validation Check | Result |
|---|---:|
| Total chart tasks | 24 |
| Reference and image validation passed | 24/24 |
| Adversarial fault scenarios detected | 4/4 |
| Automated tests passed | 8/8 |

The four adversarial scenarios detected were:

- Incorrect reference answer
- Missing image
- Duplicate task ID
- Ambiguous tie

The automated test suite covers dataset loading, task validation, incorrect answers, tied values, missing images, duplicate IDs, and generator behaviour.

## 6. Model Evaluation Results

**Evaluated model:** NVIDIA Nemotron 3.5 Super VL  
**Evaluation platform:** OpenRouter  
**Charts evaluated:** 24  
**Questions evaluated:** 144

### Overall Performance

| Metric | Result |
|---|---:|
| Correct answers | 119 |
| Incorrect answers | 25 |
| Total questions | 144 |
| Accuracy | **82.64%** |

### Results by Chart Family

| Chart Family | Correct | Questions | Accuracy |
|---|---:|---:|---:|
| Vertical bar | 31 | 36 | 86.11% |
| Horizontal bar | 32 | 36 | 88.89% |
| Line | 27 | 36 | 75.00% |
| Lollipop | 29 | 36 | 80.56% |

### Results by Question Type

| Question Type | Correct | Questions | Accuracy |
|---|---:|---:|---:|
| Highest category | 24 | 24 | 100.00% |
| Second highest | 24 | 24 | 100.00% |
| Value lookup | 24 | 24 | 100.00% |
| Absolute difference | 18 | 24 | 75.00% |
| Count above threshold | 10 | 24 | 41.67% |
| Total value | 16 | 18 | 88.89% |
| Largest step change | 3 | 6 | 50.00% |

## 7. Findings and Error Analysis

The evaluation revealed different performance levels across chart families and question types.

### Strengths

The model achieved 100% accuracy on:

- Highest-category questions
- Second-highest-category questions
- Value-lookup questions

These results indicate strong performance on the direct ranking and value-reading questions in this dataset.

### Weaknesses

The weakest chart family in this evaluation was the line-chart family, with 75.00% accuracy.

The weakest question type was count-above-threshold, with 41.67% accuracy. Largest-step-change questions also showed room for improvement, with 50.00% accuracy.

These findings identify areas where the evaluated model struggled on this particular dataset.

They should not be interpreted as general claims about all vision-language models or all forms of visual reasoning.

## 8. Repository Structure

```text
ZeroShortcut/
├── data/
│   ├── visual_tasks_v2.json
│   └── images_v2/
├── evaluations/
│   ├── README.md
│   └── nemotron/
├── evidence/
│   ├── screenshots/
│   └── validation_test_run.log
├── reports/
├── zeroshortcut/
│   ├── __init__.py
│   └── core.py
├── tests/
│   └── test_pipeline.py
├── notebooks/
│   └── ZeroShortcut_Visual_Task_Factory.ipynb
├── generate.py
├── validate.py
├── adversarial_test.py
├── create_report.py
├── evaluate_openrouter.py
├── requirements.txt
├── BENCHMARK_RESULTS.md
├── PACKAGE_MANIFEST.json
└── README.md
```

## 9. Running the Project

Use Python 3.10 or later.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run reference validation:

```bash
python validate.py
```

Run adversarial validation:

```bash
python adversarial_test.py
```

Generate consolidated reports:

```bash
python create_report.py
```

Run automated tests:

```bash
python -m pytest -q
```

### Regenerate the Dataset

```bash
python generate.py --output-dir data --count 24 --seed 20261123
```

Then run the validation commands again.

The line-chart generator resamples values until the largest consecutive absolute change is unique, preventing an ambiguous largest-step-change reference answer.

Regeneration overwrites the packaged JSON and PNG files. Keep a backup before changing the seed or task count.

## 10. Re-running Model Evaluation

The project includes `evaluate_openrouter.py`, which uses the OpenRouter chat-completions endpoint and the model:

`nvidia/nemotron-3.5-super-vl:free`

Set the API key as an environment variable. Never hard-code or commit API keys.

Example:

```bash
export OPENROUTER_API_KEY="your-key"
python evaluate_openrouter.py --resume
```

The evaluator saves raw responses and scored files per task and skips tasks that already have six saved answers.

Read `evaluations/README.md` before running the evaluator. Free-model availability and quotas may change.

## 11. Evidence and Reports

The repository includes the following evaluation evidence:

- `reports/validation_report_v2.json` – reference validation results.
- `reports/adversarial_validation_v2.json` – adversarial validation results.
- `reports/nemotron_final_benchmark.json` – final model evaluation results.
- `reports/nemotron_detailed_results.csv` – per-question scoring.
- `evaluations/nemotron/` – raw model responses and scored task records.
- `evidence/screenshots/` – screenshots of the generated chart gallery.
- `tests/test_pipeline.py` – automated pipeline tests.

## 12. Limitations and Future Work

The current benchmark has the following limitations:

- The dataset is synthetic and contains only 24 charts.
- Only four chart families are included.
- Only one external vision-language model has been evaluated.
- The reported accuracy applies only to this dataset, model configuration, prompt, evaluation procedure, and scoring rules.
- No second-model comparison or broad external generalisation study has been completed.

Future work could expand chart and question diversity, compare additional vision-language models, and evaluate carefully verified real-world charts where usage rights permit.

## 13. Conclusion

ZeroShortcut provides a reproducible pipeline for generating synthetic visual chart tasks, validating reference answers, testing validation reliability through adversarial cases, and evaluating a vision-language model.

The completed evaluation demonstrates measurable differences in model performance across chart families and question types. The results also identify specific areas where further evaluation and improvement are needed.

The project focuses on transparent task generation, independently calculated reference answers, reproducible validation, and inspectable model-evaluation evidence.
