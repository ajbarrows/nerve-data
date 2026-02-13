"""
Module for loading BIDS-formatted parquet files into a SQLite database.
"""

import sqlite3
from pathlib import Path
import pandas as pd


def get_primary_keys(df: pd.DataFrame) -> list[str]:
    """Determine primary keys based on available columns."""
    if "participant_id" in df.columns and "session_id" in df.columns:
        return ["participant_id", "session_id"]
    elif "participant_id" in df.columns:
        return ["participant_id"]
    return []


def load_parquet_to_db(
    data_dir: str | Path,
    db_path: str | Path,
    if_exists: str = "replace",
) -> sqlite3.Connection:
    """
    Load all parquet files from a directory into a SQLite database.

    Parameters
    ----------
    data_dir : str or Path
        Directory containing .parquet files
    db_path : str or Path
        Path for the SQLite database file
    if_exists : str
        How to handle existing tables: 'replace', 'append', or 'fail'

    Returns
    -------
    sqlite3.Connection
        Connection to the created database
    """
    data_dir = Path(data_dir)
    db_path = Path(db_path)
    parquet_files = list(data_dir.glob("*.parquet"))

    # Create parent directories if they don't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)

    for pq_file in parquet_files:
        table_name = pq_file.stem
        df = pd.read_parquet(pq_file)
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)

        # Add primary key constraint via index
        keys = get_primary_keys(df)
        if keys:
            key_cols = ", ".join(keys)
            idx_name = f"idx_{table_name}_pk"
            conn.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({key_cols})")

    conn.commit()
    return conn


def join_tables(
    conn: sqlite3.Connection,
    tables: list[str],
    how: str = "inner",
) -> pd.DataFrame:
    """
    Join multiple tables on their common primary keys.

    Parameters
    ----------
    conn : sqlite3.Connection
        Database connection
    tables : list of str
        Table names to join
    how : str
        Join type: 'inner', 'left', 'outer'

    Returns
    -------
    pd.DataFrame
        Joined result
    """
    if not tables:
        raise ValueError("Must provide at least one table")

    if len(tables) == 1:
        return pd.read_sql(f"SELECT * FROM {tables[0]}", conn)

    # Determine join keys for each table
    table_keys = {}
    for table in tables:
        df = pd.read_sql(f"SELECT * FROM {table} LIMIT 1", conn)
        table_keys[table] = get_primary_keys(df)

    # Build join query
    base = tables[0]
    query = f"SELECT * FROM {base}"

    join_type = {"inner": "INNER JOIN", "left": "LEFT JOIN", "outer": "LEFT JOIN"}[how]

    for table in tables[1:]:
        base_keys = table_keys[base]
        table_key = table_keys[table]
        common_keys = [k for k in base_keys if k in table_key]

        if not common_keys:
            raise ValueError(f"No common keys between {base} and {table}")

        on_clause = " AND ".join(f"{base}.{k} = {table}.{k}" for k in common_keys)
        query += f" {join_type} {table} ON {on_clause}"

    return pd.read_sql(query, conn)
