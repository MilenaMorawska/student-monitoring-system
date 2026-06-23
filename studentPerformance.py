#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Analyses student performance using assessment data stored in an SQLite database.

This module provides tools to:
- Load assessment tables from an SQLite database into Pandas DataFrames
- Standardise question-level scores to percentages based on known maximum scores
- Compute a student’s absolute performance per question
- Compute relative performance compared to the class mean
- Format internal assessment names into clearer display labels
- Display performance results in a readable format
- Visualise absolute and relative performance using Matplotlib

Typical usage example:

    manager = StudentPerformanceManager("CWDatabase.db")
    df = manager.load_test_table("Test1")
    df = manager.standardise_scores(df, "Test1", MAX_SCORES)
    perf_df = manager.student_performance(df, researcher_id=15)
    manager.display_performance(perf_df, "Test1", researcher_id=15)
    manager.plot_performance(perf_df, "Test1", researcher_id=15)

Author:
    F517819

Created:
    03/01/2026

Last Updated:
    13/01/2026
"""


# In[16]:


import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


class StudentPerformanceManager:
    """
    A class to manage student performance analysis from SQLite assessment tables.

    Attribute:
        db_path (str): Path to the SQLite database file containing assessment tables.
    """

    def __init__(self, db_path="CWDatabase.db"):
        """
        Initializes the manager with the SQLite database path.

        Args:
            db_path (str, optional): Path to the SQLite database file.
                Defaults to "CWDatabase.db".
        """
        self.db_path = db_path


    def load_test_table(self, table_name):
        """
        Loads an assessment table from the SQLite database into a Pandas DataFrame.

        Args:
            table_name (str): Name of the assessment table to load (e.g., "Test1", "SumTest").

        Returns:
            pd.DataFrame: DataFrame containing all rows and columns from the selected table.
        """
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(f'SELECT * FROM "{table_name}"', conn)


    def standardise_scores(self, df, test_name, max_scores_dict):
        """
        Standardises question scores to percentages (0–100) using max scores.

        This converts each question column using:
            (score / max_score) * 100

        Args:
            df (pd.DataFrame): DataFrame containing student results for one assessment.
            test_name (str): Name of the assessment (must exist in max_scores_dict).
            max_scores_dict (dict[str, dict[str, int | float]]):
                Dictionary where each test name maps to a dictionary of question max scores

        Returns:
            pd.DataFrame: A copy of the DataFrame with standardised question columns.
        """
        df_clean = df.copy()

        if test_name not in max_scores_dict:
            raise ValueError(f"Max scores not found for test '{test_name}'")

        for col, max_score in max_scores_dict[test_name].items():
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
                df_clean[col] = (df_clean[col] / max_score) * 100
            else:
                print(f"Warning: Column '{col}' not found in {test_name}")

        return df_clean


    def student_performance(self, df, researcher_id):
        """
        Computes absolute and relative performance for a single student.

        Absolute performance:
            - Student's standardised score (%) for each question.

        Relative performance:
            - Student's score (%) minus the class mean (%) for each question.

        Args:
            df (pd.DataFrame): Standardised assessment DataFrame (question columns already %).
            researcher_id (int): Student identifier stored as [research id].

        Returns:
            pd.DataFrame | None:
                DataFrame indexed by question (e.g., Q1, Q2, ...), with columns:
                    - "Absolute (%)"
                    - "Relative vs Class Mean (%)"
                Returns None if the student is not found.
        """
        question_cols = [c for c in df.columns if str(c).lower().startswith("q")]

        student_row = df[df["research id"] == researcher_id]
        if student_row.empty:
            return None

        abs_perf = student_row[question_cols].iloc[0]
        rel_perf = abs_perf - df[question_cols].mean(numeric_only=True)

        perf_df = pd.DataFrame({
            "Absolute (%)": abs_perf.round(2),
            "Relative vs Class Mean (%)": rel_perf.round(2)
        })

        return perf_df


    def format_test_name(self, test_name: str):
        """
        Formats internal table names into nicer display names.

        Example:
            "Test1" -> "Test 1"

        Args:
            test_name (str): Raw table name used in the database.

        Returns:
            str: Nicely formatted test name for display.
        """
        if test_name.lower().startswith("test") and test_name[4:].isdigit():
            return f"Test {test_name[4:]}" 

        if test_name == "MockTest":
            return "Mock Test"
        if test_name == "SumTest":
            return "Sum Test"

        return test_name


    def display_performance(self, perf_df, test_name, researcher_id):
        """
        Displays the performance results in a readable format.

        Args:
            perf_df (pd.DataFrame | None): Output from student_performance().
            test_name (str): Name of the assessment.
            researcher_id (int): Student identifier for display.
        """
        nice_name = self.format_test_name(test_name)

        if perf_df is None:
            print(f"No data found for researcher ID {researcher_id} in {nice_name}.")
            return

        print(f"\nPerformance for {nice_name} (Researcher ID {researcher_id}):")
        print(perf_df.to_string())


    def plot_performance(self, perf_df, test_name, researcher_id):
        """
        Plots absolute and relative performance per question.

        Args:
            perf_df (pd.DataFrame | None): Output from student_performance().
            test_name (str): Name of the assessment.
            researcher_id (int): Student identifier used in plot titles.
        """
        if perf_df is None:
            return

        nice_name = self.format_test_name(test_name)

        # Absolute performance plot
        plt.figure(figsize=(10, 4))
        plt.bar(perf_df.index, perf_df["Absolute (%)"])
        plt.ylim(0, 110)
        plt.ylabel("Absolute Score (%)")
        plt.title(f"Absolute Performance for {nice_name} (ID {researcher_id})")
        plt.show()

        # Relative performance plot
        plt.figure(figsize=(10, 4))
        plt.bar(perf_df.index, perf_df["Relative vs Class Mean (%)"])
        plt.axhline(0, color="black", linewidth=1)
        plt.ylabel("Relative Performance (%)")
        plt.title(f"Relative Performance vs Class Mean for {nice_name} (ID {researcher_id})")
        plt.show()


# ----------------------
# Testing block
# ----------------------
if __name__ == "__main__":

    # Example max scores dictionary for testing
    MAX_SCORES = {
        "Test1": {"Q1": 1, "Q2": 1, "Q3": 1, "Q4": 1, "Q5": 1, "Q6": 1},
        "Test2": {"Q1": 1, "Q2": 1, "Q3": 1, "Q4": 2, "Q5": 1, "Q6": 1},
    }

    manager = StudentPerformanceManager("CWDatabase.db")

    test_name = "Test1"
    researcher_id = 138

    df = manager.load_test_table(test_name)
    df_std = manager.standardise_scores(df, test_name, MAX_SCORES)
    perf_df = manager.student_performance(df_std, researcher_id)

    manager.display_performance(perf_df, test_name, researcher_id)
    manager.plot_performance(perf_df, test_name, researcher_id)


# In[ ]:




