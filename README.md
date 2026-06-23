# Student Monitoring System

## Author

Milena Morawska

GitHub: https://github.com/MilenaMorawska

---
## Overview
The **Student Monitoring System** is designed to process and analyse student test result data from CSV files.  
It provides tools for evaluating student performance, identifying underperforming students, and supporting academic monitoring through a simple interactive interface.

The system is intended for use within a Jupyter Notebook environment, using interactive widgets for menu navigation.

---

## Features

- Load and process student test result CSV files
- Analyse overall student performance
- Identify underperforming students
- Modular system design for scalability
- Interactive Jupyter Notebook menu (ipywidgets)
- Error handling for missing or invalid data files

---

## Requirements

All project dependencies are provided in the `requirements.txt` file 

- Python 3.12
- pandas
- IPython
- Jupyter Notebook 6
- ipywidgets
- Graphviz (python-graphviz)
- matplotlib

---

## Installation

1) Clone the repository:

```bash
git clone https://github.com/MilenaMorawska/student-monitoring-system.git
cd student-monitoring-system
```
2) Install the required dependencies:

```bash
pip install -r requirements.txt
```
3) Launch Jupyter Notebook:

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

