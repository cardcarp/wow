# Contributing

Thank you for helping maintain this data!

Before jumping in, please review these community resources:

*   **[Join Discord](https://discord.gg/9ASXsqeUWr):** Discuss structure and data accuracy.

## 🌭 Local Setup

Before submitting a pull-request, please test your changes locally to ensure they compile correctly.

1. Clone repository.
2. Install required Python dependencies: `pip install .`
3. Run the compile script to verify your YAML syntax and schema compliance: `python scripts/compile.py`

## 🪲 Automated Validation

Every pull-request is automatically validated against the schema via GitHub Actions. If the pipeline fails, your pull-request cannot be merged. You can view the exact line causing the error by clicking "Details" on the failed GitHub-Action check.
