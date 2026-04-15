# AI Curriculum Analysis × JAAT

This demo applies the [JAAT](https://github.com/Job-Ad-Research-at-QSB-LUC/JAAT) (Job Ad Analysis Toolkit) to a dataset of 113 publicly available AI course syllabi. It demonstrates how JAAT's `TaskMatch`, `SkillMatch`, 'ConceptSearch' and `AIMatch` modules can be used to analyze educational content and map it to standardized labor market features.

## Quick Start

1. Open the [AI_Curriculum_JAAT_Analysis.ipynb](AI_Curriculum_JAAT_Analysis.ipynb) notebook.
2. Run all cells to install JAAT and perform the analysis.

## Modules Used

- **TaskMatch**: Maps course content to O*NET standardized work tasks.
- **SkillMatch**: Maps course content to ESCO/EuropaCodes skills.
- **AIMatch**: Identifies specific AI-related tasks and requirements, providing an "AI score" for each course.
- **ConceptSearch**: Results of running 590 unique AI keywords from the literature.

## Data

The dataset `AI_course_syllabi_.xlsx` contains syllabi from various AI courses worldwide, including descriptions, topics, and learning outcomes.

### Data Citation
The original dataset author:

```
@misc{ahmed_abdulhakim_2024,
	title={AI Course Syllabi},
	url={https://www.kaggle.com/dsv/9147970},
	DOI={10.34740/KAGGLE/DSV/9147970},
	publisher={Kaggle},
	author={Ahmed Abdulhakim},
	year={2024}
}
```
