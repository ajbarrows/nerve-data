"""
SQLite database backed by BIDS-formatted parquet files.
"""

import sqlite3
from pathlib import Path
import pandas as pd


class BIDSDatabase:
    """
    Manages a SQLite database populated from BIDS-adjacent parquet files.

    Supports use as a context manager::

        with BIDSDatabase("my.db") as db:
            db.load("/path/to/parquets")
            df = db.join(["participants", "sessions"])
    """

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> "BIDSDatabase":
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.db_path)
        return self

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "BIDSDatabase":
        return self.connect()

    def __exit__(self, *args):
        self.close()

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self.connect()
        return self._conn

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _primary_keys(df: pd.DataFrame) -> list[str]:
        if "participant_id" in df.columns and "session_id" in df.columns:
            return ["participant_id", "session_id"]
        elif "participant_id" in df.columns:
            return ["participant_id"]
        return []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, data_dir: str | Path, if_exists: str = "replace") -> "BIDSDatabase":
        """Load all parquet files from data_dir into the database as tables."""
        for pq_file in Path(data_dir).glob("*.parquet"):
            table_name = pq_file.stem
            df = pd.read_parquet(pq_file)
            df.to_sql(table_name, self.conn, if_exists=if_exists, index=False)

            keys = self._primary_keys(df)
            if keys:
                key_cols = ", ".join(keys)
                idx_name = f"idx_{table_name}_pk"
                self.conn.execute(
                    f"CREATE UNIQUE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({key_cols})"
                )

        self.conn.commit()
        return self

    def join(self, tables: list[str], how: str = "inner") -> pd.DataFrame:
        """
        Join multiple tables on their shared primary keys.

        Parameters
        ----------
        tables : list of str
            Table names to join, in order. The first table is the base.
        how : str
            'inner', 'left', or 'outer'.
        """
        if not tables:
            raise ValueError("Must provide at least one table")
        if len(tables) == 1:
            return pd.read_sql(f"SELECT * FROM {tables[0]}", self.conn)

        table_keys = {
            t: self._primary_keys(pd.read_sql(f"SELECT * FROM {t} LIMIT 1", self.conn))
            for t in tables
        }

        join_sql = {"inner": "INNER JOIN", "left": "LEFT JOIN", "outer": "LEFT JOIN"}[how]
        base = tables[0]
        query = f"SELECT * FROM {base}"

        for table in tables[1:]:
            common = [k for k in table_keys[base] if k in table_keys[table]]
            if not common:
                raise ValueError(f"No common keys between {base} and {table}")
            on_clause = " AND ".join(f"{base}.{k} = {table}.{k}" for k in common)
            query += f" {join_sql} {table} ON {on_clause}"

        return pd.read_sql(query, self.conn)
