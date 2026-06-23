#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Preprocesses student assessment CSV files and stores the cleaned results in an SQLite database.

This module provides tools to load raw assessment data from CSV files, clean and standardise
column names, handle missing values, retain each student’s highest score per assessment,
adjust all grades to a scale of 100, and save the processed data into an SQLite database.

Typical usage example:

    manager = CWPreprocessingManager("CWDatabase.db")
    df = manager.load_csv("Formative_Test_1.csv")
    df = manager.clean_columns(df)
    df = manager.fill_missing_values(df)
    df = manager.retain_highest_score(df)
    df = manager.adjust_grade(df, max_score=6)
    manager.save_tables({"Test1": df})

Author:
    F517819

Created:
    07/12/2025

Last Updated:
    13/01/2026
"""


# In[4]:


import pandas as pd
import sqlite3


class CWPreprocessingManager:
    """
    A class to manage preprocessing and database storage of student assessment data.

    Attribute:
        db_path (str): Path to the SQLite database file used for storage.
    """

    def __init__(self, db_path="CWDatabase.db"):
        """
        Initializes the database manager with the SQLite database path.

        Args:
            db_path (str, optional): Path to the SQLite database file used for storage.
                Defaults to "CWDatabase.db".
        """
        self.db_path = db_path

    def load_csv(self, path):
        """
        Load a CSV file into a Pandas DataFrame.

        Args:
            path (str): File path to the CSV file.

        Returns:
            pd.DataFrame: DataFrame containing the CSV contents.
        """
        return pd.read_csv(path)

    def clean_columns(self, df):
        """
        Cleans and standardises column names in an assessment DataFrame.
        - Removes max-score suffixes from question headers (e.g. "Q 1 /100" -> "Q 1").
        - Converts question columns to a consistent format (e.g. "Q 1" -> "Q1").
        - Strips leading and trailing whitespace.

        Args:
            df (pd.DataFrame): Raw DataFrame loaded from a CSV file.

        Returns:
            pd.DataFrame: A cleaned copy of the DataFrame with standardised column names.
        """
        df_clean = df.copy()
        df_clean.columns = (
            df_clean.columns
            .str.replace(r"/\s*\d+", "", regex=True)     # remove "/100" or "/ 100"
            .str.replace(r"Q\s*(\d+)", r"Q\1", regex=True)  # "Q 1" -> "Q1"
            .str.strip()
        )
        return df_clean

    def clean_student_rate_columns(self, df):
        """
        Cleans and standardises column names for StudentRate-style survey data.
        - Renames a known survey column to a clearer full name.
        - Ensures all non-ID columns end with a question mark.

        Args:
            df (pd.DataFrame): Input StudentRate DataFrame.

        Returns:
            pd.DataFrame: A cleaned copy of the StudentRate DataFrame with standardised column names.
        """
        df_clean = df.copy()
        rename_map = {
            "Can you please specify the programming language you know which a":
            "Can you please specify the programming languages you know"
        }
        df_clean.rename(columns=rename_map, inplace=True)

        df_clean.columns = [
            col if col.lower().strip() == "research id" else col.rstrip(" ?") + " ?"
            for col in df_clean.columns
        ]
        return df_clean

    def fill_missing_values(self, df, value=0):
        """
        Replaces missing values in a DataFrame.

        Args:
            df (pd.DataFrame): DataFrame that may contain missing values.
            value (int or float, optional): Value used to replace missing entries.
                Defaults to 0.

        Returns:
            pd.DataFrame: A cleaned copy of the DataFrame with missing values filled.
        """
        df_clean = df.copy()
        df_clean.fillna(value, inplace=True)
        return df_clean

    def retain_highest_score(self, df):
        """
        Retains only the highest Grade per student.
        - If a student has multiple rows for the same test, the row with the highest
          Grade is kept and all other attempts are discarded.

        Args:
            df (pd.DataFrame): DataFrame containing student results.

        Returns:
            pd.DataFrame: A cleaned copy of the DataFrame with at most one row per research id.

        Notes:
            This step is only applied if both "research id" and "Grade" columns exist.
            If either column is missing, the DataFrame is returned unchanged.
        """
        df_clean = df.copy()
        if {"research id", "Grade"}.issubset(df_clean.columns):
            df_clean.sort_values("Grade", ascending=False, inplace=True)
            df_clean = df_clean.drop_duplicates("research id", keep="first")
        return df_clean

    def drop_unnecessary_columns(self, df, columns_to_remove=None):
        """
        Removes redundant columns from an assessment DataFrame.
        - Excludes the administrative columns used in CSV exports (e.g., State, Time taken).

        Args:
            df (pd.DataFrame): DataFrame.
            columns_to_remove (list[str], optional): Column names to remove.
                Defaults to ["State", "Time taken"].

        Returns:
            pd.DataFrame: A cleaned copy of the DataFrame with redundant columns removed.
        """
        df_clean = df.copy()
        if columns_to_remove is None:
            columns_to_remove = ["State", "Time taken"]
        df_clean.drop(columns=columns_to_remove, errors="ignore", inplace=True)
        return df_clean

    def convert_types(self, df):
        """
        Converts DataFrame columns to consistent data types.
        - Converts ID-like columns to nullable integers.
        - Converts Grade and question columns to numeric values.
        - Converts remaining columns to strings.

        Args:
            df (pd.DataFrame): DataFrame with mixed or inconsistent types.

        Returns:
            pd.DataFrame: A cleaned copy of the DataFrame with standardised column types.
        """
        df_clean = df.copy()
        for col in df_clean.columns:
            col_lower = col.lower()
            if "id" in col_lower:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").astype("Int64")
            elif "grade" in col_lower or col_lower.startswith("q"):
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            else:
                df_clean[col] = df_clean[col].astype("string")
        return df_clean

    def adjust_grade(self, df, max_score):
        """
        Adjusts raw grades to a standard 0–100 scale.
        - Recalculates Grade using: (Grade / max_score) * 100.

        Args:
            df (pd.DataFrame): Cleaned DataFrame containing a "Grade" column.
            max_score (int or float): Maximum possible raw score for the assessment.

        Returns:
            pd.DataFrame: A formatted copy of the DataFrame with the adjusted Grade values.
        """
        formatted_clean_df = df.copy()
        formatted_clean_df["Grade"] = pd.to_numeric(formatted_clean_df["Grade"], errors="coerce")
        formatted_clean_df["Grade"] = (formatted_clean_df["Grade"] / max_score) * 100
        return formatted_clean_df

    def save_tables(self, tables: dict):
        """
        Saves multiple DataFrames as separate tables in an SQLite database.
        - Uses a basic data model: one database table per DataFrame.
        - Replaces tables if they already exist.

        Args:
            tables (dict[str, pd.DataFrame]): Mapping of table name to DataFrame to save.
        """
        conn = sqlite3.connect(self.db_path)
        for name, df in tables.items():
            df.to_sql(name, conn, if_exists="replace", index=False)
        conn.close()


# ----------------------
# Testing block
# ----------------------
if __name__ == "__main__":
    manager = CWPreprocessingManager("CWDatabase.db")

    csv_paths = [
        r"C:\Users\milen\OneDrive - Loughborough University\cop504cw\TestResults\Formative_Test_1.csv",
        r"C:\Users\milen\OneDrive - Loughborough University\cop504cw\TestResults\Formative_Test_2.csv",
        r"C:\Users\milen\OneDrive - Loughborough University\cop504cw\TestResults\Formative_Test_3.csv",
        r"C:\Users\milen\OneDrive - Loughborough University\cop504cw\TestResults\Formative_Test_4.csv",
        r"C:\Users\milen\OneDrive - Loughborough University\cop504cw\TestResults\Formative_Mock_Test.csv",
        r"C:\Users\milen\OneDrive - Loughborough University\cop504cw\TestResults\SumTest.csv"
    ]

    # Load CSVs
    dfs_original = []
    missing_files = []

    for path in csv_paths:
        try:
            dfs_original.append(manager.load_csv(path))
        except FileNotFoundError:
            missing_files.append(path)

    if missing_files:
        for path in missing_files:
            print(f"❌ File not found: {path}")

    # Clean dfs
    dfs_cleaned = [manager.clean_columns(df) for df in dfs_original]
    dfs_cleaned = [manager.fill_missing_values(df) for df in dfs_cleaned]
    dfs_cleaned = [manager.retain_highest_score(df) for df in dfs_cleaned]
    dfs_cleaned = [manager.drop_unnecessary_columns(df) for df in dfs_cleaned]
    dfs_cleaned = [manager.convert_types(df) for df in dfs_cleaned]

    # Adjust Grades to scale of 100
    max_scores = [6, 7, 6, 10, 100, 100]
    table_names = ["Test1", "Test2", "Test3", "Test4", "MockTest", "SumTest"]

    dfs_scaled = [
        manager.adjust_grade(df_clean, max_score)
        for df_clean, max_score in zip(dfs_cleaned, max_scores)
    ]

    print("✅ All preprocessing steps completed successfully.\n")

    # Save Tables to Database
    tables_to_save = dict(zip(table_names, dfs_scaled))
    manager.save_tables(tables_to_save)

    print("✅ All tables saved to database.\n")

    # Verify Database
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    db_tables = cursor.fetchall()
    conn.close()

    print("Tables in the database:")
    for t in db_tables:
        print(f"- {t[0]}")

    print("\n✅ Preprocessing & database test complete.")


# In[ ]:




