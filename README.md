# JAAT Demos

Demonstrations of [JAAT](https://github.com/Job-Ad-Research-at-QSB-LUC/JAAT) (Job Ad Analysis Toolkit) applied to different public text sources. These notebooks show 1) how to use JAAT, 2) how JAAT tools are validated when public sources of data are available, and 3) how JAAT's modules generalize beyond job advertisements to other related text.

**Try JAAT interactively on 1 Job Posting at a Time:** [JAAT Demo on Hugging Face](https://huggingface.co/spaces/pnorlander/JAAT_DEMO)

## Demos

| Demo | Module | Public Data | Colab |
|------|--------|------|-------|
| [OSHA Accident Narratives](osha_accident_taskmatch/) | TaskMatch | 1,000 OSHA investigations | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pnorlander/JAAT_Demos/blob/main/osha_accident_taskmatch/OSHA_TaskMatch_Demo.ipynb) |
| [TitleMatch Validation](titlematch_validation/) | TitleMatch | 65,645 LCA title-code pairs | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pnorlander/JAAT_Demos/blob/main/titlematch_validation/TitleMatch_Validation.ipynb) |
| [AI Curriculum Analysis](ai_curriculum/) | SkillMatch, TaskMatch, AIMatch | 113 AI course syllabi | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pnorlander/JAAT_Demos/blob/main/ai_curriculum/AI_Curriculum_JAAT_Analysis.ipynb) |

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
