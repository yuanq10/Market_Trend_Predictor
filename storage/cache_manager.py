"""
SQLite-backed cache for OHLCV price history.

Schema
------
price_history : one row per (ticker, date) — daily OHLCV
fetch_meta    : one row per ticker — ISO timestamp of last successful fetch
"""

import os
import sys
import sqlite3
from datetime import date, timedelta, datetime

import pandas as pd

# Place cache.db alongside settings.json / alerts.json
if getattr(sys, "frozen", False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.dirname(__file__))

CACHE_DB = os.path.join(_BASE, "data", "cache.db")

_initialized = False


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)
    conn = sqlite3.connect(CACHE_DB)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables if they don't exist. Safe to call multiple times."""
    global _initialized
    if _initialized:
        return
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                ticker  TEXT    NOT NULL,
                date    TEXT    NOT NULL,
                open    REAL,
                high    REAL,
                low     REAL,
                close   REAL,
                volume  INTEGER,
                PRIMARY KEY (ticker, date)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fetch_meta (
                ticker        TEXT PRIMARY KEY,
                last_fetched  TEXT NOT NULL
            )
        """)
    _initialized = True


# ------------------------------------------------------------------
# Trade-date logic
# ------------------------------------------------------------------

def last_trade_date() -> date:
    """
    Return the most recent weekday (Mon–Fri).
    Does not account for public holidays — acceptable as an edge case.
    """
    today = date.today()
    wd = today.weekday()   # 0=Mon … 6=Sun
    if wd == 5:            # Saturday → Friday
        return today - timedelta(days=1)
    if wd == 6:            # Sunday → Friday
        return today - timedelta(days=2)
    return today


# ------------------------------------------------------------------
# Cache freshness
# ------------------------------------------------------------------

def is_cache_fresh(ticker: str) -> bool:
    """Return True if ticker was fetched on or after the last trade date."""
    init_db()
    try:
        with _connect() as conn:
            row = conn.execute(
                "SELECT last_fetched FROM fetch_meta WHERE ticker = ?", (ticker,)
            ).fetchone()
        if not row:
            return False
        fetched_date = datetime.fromisoformat(row[0]).date()
        return fetched_date >= last_trade_date()
    except Exception:
        return False


def get_last_fetched(ticker: str) -> datetime | None:
    """Return the last-fetched datetime for a ticker, or None."""
    init_db()
    try:
        with _connect() as conn:
            row = conn.execute(
                "SELECT last_fetched FROM fetch_meta WHERE ticker = ?", (ticker,)
            ).fetchone()
        return datetime.fromisoformat(row[0]) if row else None
    except Exception:
        return None


# ------------------------------------------------------------------
# Read / write
# ------------------------------------------------------------------

def save_price_history(ticker: str, df: pd.DataFrame):
    """Upsert OHLCV rows and update fetch_meta timestamp."""
    init_db()
    rows = []
    for dt, row in df.iterrows():
        rows.append((
            ticker,
            dt.strftime("%Y-%m-%d"),
            float(row["Open"]),
            float(row["High"]),
            float(row["Low"]),
            float(row["Close"]),
            int(row["Volume"]),
        ))
    with _connect() as conn:
        conn.executemany(
            """INSERT OR REPLACE INTO price_history
               (ticker, date, open, high, low, close, volume)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        conn.execute(
            """INSERT OR REPLACE INTO fetch_meta (ticker, last_fetched)
               VALUES (?, ?)""",
            (ticker, datetime.now().isoformat()),
        )


def load_price_history(ticker: str) -> pd.DataFrame | None:
    """Return cached OHLCV DataFrame for ticker, or None if not cached."""
    init_db()
    try:
        with _connect() as conn:
            rows = conn.execute(
                """SELECT date, open, high, low, close, volume
                   FROM price_history
                   WHERE ticker = ?
                   ORDER BY date""",
                (ticker,),
            ).fetchall()
        if not rows:
            return None
        df = pd.DataFrame(rows, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
        return df
    except Exception:
        return None


# ------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------

def prune_old_rows(days: int = 90):
    """Delete price_history rows older than `days` days."""
    init_db()
    cutoff = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")
    with _connect() as conn:
        conn.execute(
            "DELETE FROM price_history WHERE date < ?", (cutoff,)
        )


def prune_removed_tickers(current_tickers: list[str]):
    """
    Delete price_history and fetch_meta rows for tickers no longer
    in the watchlist.
    """
    init_db()
    if not current_tickers:
        return
    placeholders = ",".join("?" * len(current_tickers))
    with _connect() as conn:
        conn.execute(
            f"DELETE FROM price_history WHERE ticker NOT IN ({placeholders})",
            current_tickers,
        )
        conn.execute(
            f"DELETE FROM fetch_meta WHERE ticker NOT IN ({placeholders})",
            current_tickers,
        )
