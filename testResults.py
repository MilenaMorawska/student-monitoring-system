#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
Test Results Manager

Fetches, displays, and visualises student grades stored in an SQLite database.

This module provides tools to:
- Connect to an SQLite database containing assessment tables
- Retrieve a student's Grade from a specified assessment table
- Print the student's grades across multiple assessments
- Plot the grades using Matplotlib for quick visual inspection

Typical usage example:

    manager = TestResultsManager("CWDatabase.db")
    tables = ["Test1", "Test2", "Test3", "Test4", "MockTest", "SumTest"]
    researcher_id = 138
    grades = {t: manager.fetch_grade_from_table(researcher_id, t) for t in tables}
    display_grades(grades, researcher_id)
    plot_grades(grades, researcher_id)

Author:
    F517819

Created:
    03/01/2026

Last Updated:
    13/01/2026
"""


# In[6]:


import sqlite3
import matplotlib.pyplot as plt
import pandas as pd


class TestResultsManager:
    """
    A class to manage retrieval of student grades from an SQLite database.

    Attribute:
        database_path (str): Path to the SQLite database file.
    """

    def __init__(self, db_path="CWDatabase.db"):
        """
        Initializes the database manager with the SQLite database path.

        Args:
            db_path (str, optional): Path to the SQLite database file.
                Defaults to "CWDatabase.db".
        """
        self.database_path = db_path

    def fetch_grade_from_table(self, researcher_id: int, table_name: str):
        """
        Fetches the Grade value for a given student from a specific table.

        Args:
            researcher_id (int): Student identifier stored in the database as [research id].
            table_name (str): Name of the assessment table (e.g., "Test1", "SumTest").

        Returns:
            float | None: The student's grade if found, otherwise None.
        """
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            query = f'SELECT Grade FROM "{table_name}" WHERE [research id] = ?'
            cursor.execute(query, (researcher_id,))
            result = cursor.fetchone()

        return result[0] if result else None

    def display_grades(self, grades: dict[str, float | None], researcher_id: int):
        """
        Prints all available grades for a student across multiple assessment tables.

        Args:
            grades (dict[str, float | None]): Mapping of table name to grade (or None if missing).
            researcher_id (int): Student identifier for display purposes.
        """
        if all(g is None for g in grades.values()):
            print(f"No grades found for researcher ID {researcher_id}.")
            return

        df = pd.DataFrame({
            "Assessment": grades.keys(),
            "Grade": [
                round(g, 1) if g is not None else "None"
                for g in grades.values()
            ]
        })

        print(f"\nGrades for researcher ID {researcher_id}:")
        print(df.to_string(index=False))

    def plot_grades(self, grades: dict[str, float | None], researcher_id: int):
        """
        Plots a bar chart of grades for a student.

        Args:
            grades (dict[str, float | None]): Mapping of table name to grade (or None if missing).
            researcher_id (int): Student identifier for the chart title.
        """
        plt.figure(figsize=(8, 5))
        plt.bar(
            grades.keys(),
            [g if g is not None else 0 for g in grades.values()]
        )
        plt.xlabel("Assessments")
        plt.ylabel("Grade")
        plt.title(f"Grades for Researcher ID {researcher_id}")
        plt.ylim(0, 110)
        plt.show()


# ----------------------
# Testing block
# ----------------------
if __name__ == "__main__":
    manager = TestResultsManager("CWDatabase.db")

    tables = ["Test1", "Test2", "Test3", "Test4", "MockTest", "SumTest"]

    # Input for researcher id
    while True:
        try:
            researcher_id = int(input("Enter researcher ID: "))
            break
        except ValueError:
            print("Invalid input. Please enter a numeric researcher ID.")

    grades = {
        table: manager.fetch_grade_from_table(researcher_id, table)
        for table in tables
    }

    manager.display_grades(grades, researcher_id)
    manager.plot_grades(grades, researcher_id)


# In[ ]:




