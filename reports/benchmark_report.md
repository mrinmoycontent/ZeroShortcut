# ZeroShortcut – Consolidated Benchmark Report

## Dataset summary

| Metric | Result |
|---|---:|
| Visual tasks | 24 |
| Questions | 144 |
| Valid image files | 24 |
| Unique source datasets | 24 |
| Reference validation passed | 24 |
| Reference validation failed | 0 |

## Chart distribution

| Chart type | Count |
|---|---:|
| bar | 6 |
| horizontal_bar | 6 |
| line | 6 |
| lollipop | 6 |

## Question distribution

| Question type | Count |
|---|---:|
| highest_category | 24 |
| second_highest | 24 |
| value_lookup | 24 |
| absolute_difference | 24 |
| count_above_threshold | 24 |
| total_value | 18 |
| largest_step_change | 6 |

## Adversarial validation

Passed: 4/4

| Test | Result |
|---|---|
| incorrect_answer_detection | DETECTED |
| missing_image_detection | DETECTED |
| duplicate_id_detection | DETECTED |
| ambiguous_tie_detection | DETECTED |

## AI model evaluation

Completed: NVIDIA Nemotron 3.5 Super VL achieved 82.64% (119/144 correct).

## Limitations

- The current task family focuses on synthetic business-chart interpretation.
- Reference answers are compared against the source data embedded in each task.
- The adversarial suite covers four deliberately injected fault types.
- Only one external model has been evaluated; a second-model comparison remains outstanding.
- Results are specific to this synthetic chart dataset and do not establish broad visual reasoning performance.
