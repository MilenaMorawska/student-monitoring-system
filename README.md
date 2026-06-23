# student-monitoring-system

A modular, Jupyter Notebook–based application for analysing student performance data, identifying underperforming students, and managing test results using structured CSV inputs.

---
## About The Project

The **Student Monitoring System** is designed to process and analyse student test result data from CSV files.  
It provides tools for evaluating student performance, identifying underperforming students, and supporting academic monitoring through a simple interactive interface.

The system is intended for use within a **Jupyter Notebook environment**, using interactive widgets for menu navigation.

---

## Features

- Load and process student test result CSV files
- Analyse overall student performance
- Identify underperforming students
- Modular system design for scalability
- Interactive Jupyter Notebook menu (ipywidgets)
- Error handling for missing or invalid data files

---

## Installation

1) Clone the repository:

```bash
git clone https://github.com/MilenaMorawska/student-monitoring-system.git
cd student-monitoring-system
```

2) Create the Conda environment:

```bash
conda env create -f environment.yml
```

3) Activate the environment:

```bash
conda activate cop504cw
```

4) Launch Jupyter Notebook:

```bash
jupyter notebook
```

---
## General usage

This application is intended to be run within a Jupyter Notebook environment.
The interactive menu relies on ipywidgets and IPython display features.

Before running the menu:
- Ensure all required CSV files are present in the specified TestResults directory.

- Ensure all Python modules (CWPreprocessing.py, testResults.py,
  studentPerformance.py, underPerforming.py) are in the same directory as the notebook.

