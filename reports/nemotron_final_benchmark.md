# ZeroShortcut
## Final NVIDIA Nemotron Benchmark Report

### Evaluation Overview

| Metric | Result |
|---|---:|
| Model | NVIDIA Nemotron 3.5 Super VL |
| Charts evaluated | 24 |
| Questions evaluated | 144 |
| Correct answers | 119 |
| Incorrect answers | 25 |
| Overall accuracy | 82.64% |

### Performance by Chart Type

| Chart Type | Correct | Total | Accuracy |
|---|---:|---:|---:|
| bar | 31 | 36 | 86.11% |\n| horizontal_bar | 32 | 36 | 88.89% |\n| line | 27 | 36 | 75.0% |\n| lollipop | 29 | 36 | 80.56% |\n
### Performance by Question Type

| Question Type | Correct | Total | Accuracy |
|---|---:|---:|---:|
| highest_category | 24 | 24 | 100.0% |\n| second_highest | 24 | 24 | 100.0% |\n| value_lookup | 24 | 24 | 100.0% |\n| absolute_difference | 18 | 24 | 75.0% |\n| count_above_threshold | 10 | 24 | 41.67% |\n| total_value | 16 | 18 | 88.89% |\n| largest_step_change | 3 | 6 | 50.0% |\n
### Model Weakness Analysis

- Weakest chart family: line
- Weakest question category: count_above_threshold
- Total incorrect answers: 25

### Incorrect Answers

| Task | Question ID | Question Type | Expected | Model Answer |
|---|---|---|---|---|
| ZS2_003 | ZS2_003_Q4 | absolute_difference | 67 | 402 |\n| ZS2_004 | ZS2_004_Q6 | total_value | 4329 | 3529 |\n| ZS2_006 | ZS2_006_Q5 | count_above_threshold | 2 | 3 |\n| ZS2_007 | ZS2_007_Q6 | largest_step_change | Aug to Sep | Jul to Aug |\n| ZS2_008 | ZS2_008_Q4 | absolute_difference | 38 | 161 |\n| ZS2_009 | ZS2_009_Q5 | count_above_threshold | 3 | 4 |\n| ZS2_010 | ZS2_010_Q5 | count_above_threshold | 3 | 4 |\n| ZS2_010 | ZS2_010_Q6 | total_value | 3933 | 3901 |\n| ZS2_011 | ZS2_011_Q4 | absolute_difference | 500 | 236 |\n| ZS2_012 | ZS2_012_Q4 | absolute_difference | 390 | 626 |\n| ZS2_012 | ZS2_012_Q5 | count_above_threshold | 3 | 4 |\n| ZS2_013 | ZS2_013_Q4 | absolute_difference | 89 | 231 |\n| ZS2_013 | ZS2_013_Q5 | count_above_threshold | 3 | 4 |\n| ZS2_014 | ZS2_014_Q5 | count_above_threshold | 3 | 2 |\n| ZS2_015 | ZS2_015_Q5 | count_above_threshold | 3 | 4 |\n| ZS2_015 | ZS2_015_Q6 | largest_step_change | Jan to Feb | Jan and Feb |\n| ZS2_016 | ZS2_016_Q5 | count_above_threshold | 3 | 4 |\n| ZS2_017 | ZS2_017_Q5 | count_above_threshold | 2 | 3 |\n| ZS2_019 | ZS2_019_Q4 | absolute_difference | 145 | 144 |\n| ZS2_019 | ZS2_019_Q5 | count_above_threshold | 4 | 5 |\n| ZS2_020 | ZS2_020_Q5 | count_above_threshold | 2 | 3 |\n| ZS2_021 | ZS2_021_Q5 | count_above_threshold | 2 | 3 |\n| ZS2_023 | ZS2_023_Q5 | count_above_threshold | 4 | 5 |\n| ZS2_023 | ZS2_023_Q6 | largest_step_change | Aug to Sep | Jul to Aug |\n| ZS2_024 | ZS2_024_Q5 | count_above_threshold | 3 | 4 |\n
### Methodology

Each chart image was sent to the external vision model
without providing its original source data or reference answers.

The model's response was compared against the independently
generated reference answers stored in the task dataset.

Numerical answers were checked exactly.
Text answers were compared after normalization.

### Limitations

- Results apply to this synthetic business-chart dataset.
- The benchmark contains 24 charts and 144 questions.
- Accuracy on this dataset does not establish general
  visual reasoning performance.
- Results are specific to the evaluated model and configuration.
- A second-model comparison has not yet been completed.
