# student-monitoring-system



GENERAL USAGE
--------------

This application is intended to be run within a Jupyter Notebook environment.
The interactive menu relies on ipywidgets and IPython display features.

Before running the menu:
- Ensure all required CSV files are present in the specified TestResults directory.

- Ensure all Python modules (CWPreprocessing.py, testResults.py,
  studentPerformance.py, underPerforming.py) are in the same directory as the notebook.


OPTIMISATIONS
--------------

The system is designed using a modular class-based structure, which improves
maintainability and readability by separating different responsibilities into
dedicated manager classes.

Error handling is implemented to prevent the interface from crashing when required
CSV files are missing.

Database queries retrieve only the required data, reducing unnecessary processing
overhead.
