#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Identifies underperforming students using assessment data stored in an SQLite database.

This module provides tools to:
- Load assessment tables from an SQLite database
- Merge formative and summative assessment results
- Apply defined underperformance criteria based on summative and formative grades
- Identify students who require academic intervention
- Display a summary of underperforming students in a readable format
- Visualise formative and summative performance for underperforming students

Typical usage example:

    manager = UnderperformingStudentManager("CWDatabase.db")
    formative_tables = ["Test1", "Test2", "Test3", "Test4", "MockTest"]
    summative_table = "SumTest"

    merged_df = manager.merge_formative_summative(formative_tables, summative_table)
    underperforming_df = manager.identify_underperforming_students(merged_df)
    manager.print_underperforming_students(underperforming_df)
    manager.plot_underperforming_students(underperforming_df)

Author:
    F517819

Created:
    03/01/2026

Last Updated:
    13/01/2026
"""


# In[28]:


import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


class UnderperformingStudentManager:
    """
    A class to identify and visualise underperforming students using assessment data
    stored in an SQLite database.

    Underperforming criteria:
    1) Summative grade must be below 50 (Summative < 50)
    2) Minimum formative attempts = 3
    3) Among attempted formative tests, at least 2 formative grades are below 50

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

    def load_test_table(self, table_name: str) -> pd.DataFrame:
        """
        Loads an assessment table from the SQLite database into a Pandas DataFrame.

        Args:
            table_name (str): Name of the assessment table to load (e.g., "Test1", "SumTest").

        Returns:
            pd.DataFrame: DataFrame containing all rows and columns from the selected table.
        """
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(f'SELECT * FROM "{table_name}"', conn)

    def merge_formative_summative(self, formative_tables: list[str], summative_table: str):
        """
        Merges formative and summative grades into a single DataFrame.

        - Loads Grade values from each formative table and renames each Grade column to the table name (e.g., "Test1", "Test2", ...).
        - Loads the summative Grade and renames it to "Summative".
        - Merges all results on "research id" using outer joins so that missing attempts are retained.

        Args:
            formative_tables (list[str]): List of formative assessment table names.
            summative_table (str): Summative assessment table name.

        Returns:
            pd.DataFrame: Merged DataFrame containing formative grades and the summative grade per student.
        """
        with sqlite3.connect(self.db_path) as conn:

            df_sum = pd.read_sql(
                f'SELECT [research id], Grade FROM "{summative_table}"',
                conn
            )
            df_sum.rename(columns={"Grade": "Summative"}, inplace=True)


            formative_dfs = []
            for table in formative_tables:
                df = pd.read_sql(f'SELECT [research id], Grade FROM "{table}"', conn)
                df.rename(columns={"Grade": table}, inplace=True)
                formative_dfs.append(df)

            # Merge all formative tables on research id
            if formative_dfs:
                df_formative = formative_dfs[0]
                for df in formative_dfs[1:]:
                    df_formative = pd.merge(df_formative, df, on="research id", how="outer")
            else:
                df_formative = pd.DataFrame(columns=["research id"])

            # Merge formative + summative
            merged_df = pd.merge(df_formative, df_sum, on="research id", how="outer")
            return merged_df

    def identify_underperforming_students(
        self,
        df: pd.DataFrame,
        summative_max: float = 50,
        min_formative_attempts: int = 3,
        formative_low_threshold: float = 50,
        min_low_formatives: int = 2
    ):
        """
        Identifies underperforming students based on summative and formative criteria.

        Criteria:
        - Summative must be < summative_max
        - At least min_formative_attempts formative grades attempted
        - At least min_low_formatives formative grades are < formative_low_threshold

        Args:
            df (pd.DataFrame): Merged DataFrame containing formative table grades and "Summative".
            summative_max (float, optional): Summative grade must be below this value.
                Defaults to 50.
            min_formative_attempts (int, optional): Minimum number of formative attempts required.
                Defaults to 3.
            formative_low_threshold (float, optional): Threshold for a "low" formative grade.
                Defaults to 50.
            min_low_formatives (int, optional): Minimum number of low formative grades required.
                Defaults to 2.

        Returns:
            pd.DataFrame: DataFrame copy containing underperforming students only, sorted by Summative grade.
        """
        df_clean = df.copy()

        formative_cols = [c for c in df_clean.columns if c not in ["research id", "Summative"]]

        attempts_list = []
        lowest_list = []
        low_count_list = []
        passes_rule_list = []

        for _, row in df_clean.iterrows():
            attempted_grades: list[float] = []

            for col in formative_cols:
                val = row[col]
                if pd.notna(val) and val >= 0:
                    attempted_grades.append(float(val))

            attempts = len(attempted_grades)
            attempts_list.append(attempts)

            if attempts > 0:
                lowest_list.append(min(attempted_grades))

                low_count = 0
                for g in attempted_grades:
                    if g < formative_low_threshold:
                        low_count += 1
                low_count_list.append(low_count)

                passes_rule_list.append(
                    (attempts >= min_formative_attempts) and (low_count >= min_low_formatives)
                )
            else:
                lowest_list.append(None)
                low_count_list.append(0)
                passes_rule_list.append(False)

        df_clean["Formative Attempts"] = attempts_list
        df_clean["Lowest Formative"] = lowest_list
        df_clean["Formative <50 Count"] = low_count_list
        df_clean["Passes Formative Rule"] = passes_rule_list

        underperforming_rows = []
        for _, row in df_clean.iterrows():
            summative = row["Summative"]

            if pd.isna(summative) or float(summative) >= summative_max:
                continue

            if row["Passes Formative Rule"] is not True:
                continue

            underperforming_rows.append(row)

        underperforming_df = pd.DataFrame(underperforming_rows)

        if not underperforming_df.empty:
            underperforming_df.sort_values("Summative", inplace=True)
            underperforming_df.reset_index(drop=True, inplace=True)

        return underperforming_df

    def plot_underperforming_students(self, df: pd.DataFrame) -> None:
        """
        Plots formative and summative grades for each underperforming student.

        - Missing formative attempts are shown as 0.
        - The lowest attempted formative grade is highlighted in red.

        Args:
            df (pd.DataFrame): DataFrame of underperforming students (output from identify_underperforming_students()).
        """
        if df.empty:
            print("No underperforming students found.")
            return

        exclude = {
            "research id",
            "Summative",
            "Formative Attempts",
            "Lowest Formative",
            "Formative <50 Count",
            "Passes Formative Rule",
        }
        formative_cols = [c for c in df.columns if c not in exclude]

        for _, row in df.iterrows():
            student_id = row["research id"]

            grades = []
            for col in formative_cols:
                val = row[col]
                grades.append(val if pd.notna(val) else 0)

            summative = row["Summative"]
            lowest_val = row["Lowest Formative"]

            colors = []
            for val in grades:
                if pd.notna(lowest_val) and val >= 0 and val == lowest_val:
                    colors.append("crimson")
                else:
                    colors.append("tab:blue")

            plt.figure(figsize=(8, 4))
            plt.bar(
                formative_cols + ["Summative"],
                grades + [summative],
                color=colors + ["darkslateblue"],
            )
            plt.ylim(0, 110)
            plt.ylabel("Grade")
            plt.title(f"Underperforming Researcher ID: {int(student_id)}")
            plt.show()

    def print_underperforming_students(self, df: pd.DataFrame) -> None:
        """
        Prints a summary table of underperforming students with researcher IDs sorted by their grades 
        of the summative online test.

        Displays:
        - research id
        - Summative grade
        - number of formative attempts
        - count of formative grades below 50
        - lowest formative grade

        Args:
            df (pd.DataFrame): DataFrame of underperforming students.
        """
        if df.empty:
            print("No underperforming students found.")
            return

        df_print = df.copy()
        df_print["Summative"] = pd.to_numeric(df_print["Summative"], errors="coerce").round(2)
        df_print["Lowest Formative"] = pd.to_numeric(df_print["Lowest Formative"], errors="coerce").round(2)
        df_print["research id"] = pd.to_numeric(df_print["research id"], errors="coerce").astype("Int64")

        cols_to_show = [
            "research id",
            "Summative",
            "Formative Attempts",
            "Formative <50 Count",
            "Lowest Formative",
        ]
        print(df_print[cols_to_show].to_string(index=False))


# -------------------------------
# Testing block
# -------------------------------
if __name__ == "__main__":
    manager = UnderperformingStudentManager("CWDatabase.db")

    formative_tables = ["Test1", "Test2", "Test3", "Test4", "MockTest"]
    summative_table = "SumTest"

    merged_df = manager.merge_formative_summative(formative_tables, summative_table)

    underperforming_df = manager.identify_underperforming_students(
        merged_df,
        summative_max=50,
        min_formative_attempts=3,
        formative_low_threshold=50,
        min_low_formatives=2
    )

    manager.print_underperforming_students(underperforming_df)
    manager.plot_underperforming_students(underperforming_df)


# In[ ]:




