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
