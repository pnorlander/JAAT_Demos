# OSHA Accident Narratives × JAAT TaskMatch

Demonstrates how [JAAT](https://github.com/Job-Ad-Research-at-QSB-LUC/JAAT)'s `TaskMatch` module identifies standardized O\*NET work tasks in OSHA workplace accident investigation narratives.

## Quick Start

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pnorlander/JAAT_Demos/blob/main/osha_accident_taskmatch/OSHA_TaskMatch_Demo.ipynb)

Or run locally:

```bash
pip install JAAT
jupyter notebook OSHA_TaskMatch_Demo.ipynb
```

## What This Shows

- **Semantic similarity generalizes** — TaskMatch uses sentence embeddings, so it works on any text describing work activities, not just job ads
- **Transparent pipeline** — raw text → sentence splitting → TaskMatch → aggregation → visualization
- **Domain knowledge cleanup** — emergency responder tasks are separated from worker tasks with full transparency

## Data

The included sample (`data/accident_abstracts_sample.csv`) contains 1,000 randomly selected OSHA accident investigation abstracts. The full dataset (111,000+ investigations) is available from [OSHA's public data](https://www.osha.gov/data).
