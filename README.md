# Developer Disengagement in Open-Source Projects

This repository contains the full codebase and data processing pipeline for the master's thesis:

**"Multidimensional Analysis of Developer Disengagement in Open-Source Projects"**
by Chenyu Zhao, Politecnico di Milano, July 2025

---

##  Overview

This project investigates early indicators of developer disengagement in open-source software (OSS) communities using GitHub data. The study analyzes process-, product-, and people-level metrics to identify disengagement patterns and test causal relationships.

Key components include:

- Feature engineering from commits, issues, PRs, comments, and threads
- Temporal segmentation of activity
- Granger causality testing across behavioral signals
- Predictive modeling using logistic regression
- Visualizations: time series plots, network metrics...


---

## 📂 Repository Structure

├── data_preprocessing/ # Feature extraction and labeling logic
│ 
├── network_analysis/ # Interaction graph and centrality metrics
│ 
├── modeling/ # Granger causality and predictive models
│ 
├── visualization/ # trajectory plots, comparison figures
│ 
├── data/ # Sample (or anonymized) monthly activity data
└── README.md


## 📊 Key Datasets

| File | Description |
|------|-------------|
| `commits_cleaned.csv` | Commit timestamps and authors |
| `issues_cleaned.csv`  | Issue metadata and lifecycle |
| `prs_cleaned.csv`     | Pull request success and cycle time |
| `comments_cleaned.csv` | Communication volume and sentiment |
| `threads_cleaned.csv` | Developer discussion threads |
| `Final_Developer_Data_with_Sentiment.csv` | Aggregated behavioral metrics |

All data was collected from public GitHub repositories and anonymized.


## 🙋 Contact

If you have any questions, feel free to contact:

📧 cathyzhaooo@gmail.com  
