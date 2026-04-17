# Benchmarking Occupational Coding Tools Against LCA Ground Truth

This notebook benchmarks four automated occupational coding tools against publicly available employer-assigned SOC codes from U.S. Department of Labor [Labor Condition Application](https://www.dol.gov/agencies/eta/foreign-labor/programs) (LCA) filings.

## Quick Start

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pnorlander/JAAT_Demos/blob/main/titlematch_validation/TitleMatch_Validation.ipynb)

Or run locally:

```bash
pip install pandas matplotlib numpy openpyxl
jupyter notebook TitleMatch_Validation.ipynb
```

## Tools Compared

| Tool | SOC Version | Method | Source |
|------|------------|--------|--------|
| **TitleMatch** | SOC 2018 | Semantic similarity (sentence embeddings) | [JAAT](https://github.com/Job-Ad-Research-at-QSB-LUC/JAAT) |
| **SOCkit** | SOC 2018 | Classification model | [ripl-org/sockit](https://github.com/ripl-org/sockit) |
| **NIOCCS** | SOC 2018 | NIOSH/CDC web API | [csams.cdc.gov/nioccs](https://csams.cdc.gov/nioccs/) |
| **SOCcer/SOCcerNET** | SOC 2010 | Neural network classifier | [soccer.nci.nih.gov](https://soccer.nci.nih.gov/) |

SOCcer codes are crosswalked from SOC 2010 to SOC 2018 using the [BLS crosswalk](https://www.bls.gov/soc/2018/home.htm).

## Data

**65,645 unique title-code pairs** from 47,180 unique job titles across LCA filings (2008-2024). Each row pairs an employer-filed job title with an employer-assigned 6-digit SOC code and the count of filings with that combination. Titles are uncleaned.

The pre-computed analysis file (`data/all_tools_comparison.csv`) contains all four tools' codes and match indicators under multiple evaluation frames. See the notebook for details.

## Evaluation Frames

Many titles map to multiple SOC codes. Accuracy is evaluated under four frames:

| Frame | Definition |
|-------|-----------|
| **Strict** | Tool code matches this row's LCA code |
| **Any-match** | Tool code matches any LCA code for this title |
| **Best-match** | Tool code matches the most common LCA code for this title |
| **Weighted** | Strict match, weighted by filing count |

## Key Results

**6-Digit SOC (Detailed Occupation)**

| Tool | Strict | Any-match | Weighted |
|------|--------|-----------|----------|
| SOCcer | 36.2% | 48.3% | 49.1% |
| TitleMatch | 31.7% | 42.9% | 47.8% |
| NIOCCS | 30.2% | 41.5% | 47.3% |
| SOCkit | 20.8% | 31.8% | 29.8% |

**4-Digit SOC (Broad Occupation)**

| Tool | Strict | Any-match | Weighted |
|------|--------|-----------|----------|
| SOCcer | 50.2% | 62.1% | 61.5% |
| TitleMatch | 48.8% | 58.9% | 62.9% |
| NIOCCS | 47.1% | 59.3% | 62.9% |
| SOCkit | 38.0% | 48.4% | 52.0% |

**2-Digit SOC (Major Group)**

| Tool | Strict | Any-match | Weighted |
|------|--------|-----------|----------|
| NIOCCS | 65.1% | 75.4% | 77.2% |
| SOCcer | 63.5% | 72.5% | 71.0% |
| TitleMatch | 61.6% | 70.1% | 72.6% |
| SOCkit | 51.6% | 59.6% | 62.6% |

An oracle that always returns the modal code achieves 69% strict accuracy at 6-digit — the theoretical ceiling from titles alone. Rankings shift by digit level and evaluation frame. See the notebook for full analysis.

## Files

| File | Description |
|------|-------------|
| `TitleMatch_Validation.ipynb` | Analysis notebook |
| `data/all_tools_comparison.csv` | Benchmark dataset (65,645 rows, all tools + match indicators) |
| `data/soc_2010_to_2018_crosswalk.xlsx` | BLS SOC 2010-to-2018 crosswalk |
| `build_comparison.py` | Script that merges tool outputs (for reproducibility) |

## Acknowledgements

This project has received generous support from the National Labor Exchange, the Russell Sage Foundation, the Washington Center for Equitable Growth.

### Software and Data Citation
If you find `JAAT` useful in your research, please consider citing our working paper that introduces many of the abovementioned modules:

```
@article{meisenbacher2025extracting,
  title={Extracting O* NET Features from the NLx Corpus to Build Public Use Aggregate Labor Market Data},
  author={Meisenbacher, Stephen and Nestorov, Svetlozar and Norlander, Peter},
  journal={arXiv preprint arXiv:2510.01470},
  year={2025}
}
```
