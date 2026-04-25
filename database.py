import sqlite3
import json
from datetime import datetime

DB_PATH = "kreditx_reports.db"


class ReportDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS reports (
                    report_id      TEXT PRIMARY KEY,
                    created_at     TEXT NOT NULL,
                    decision       TEXT,
                    credit_score   INTEGER,
                    biz_name       TEXT,
                    biz_type       TEXT,
                    state          TEXT,
                    loan_amount    REAL,
                    form_data_json TEXT,
                    result_json    TEXT,
                    pdf_blob       BLOB NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_created_at
                    ON reports (created_at DESC);
            """)

    def save_report(self, report_id, pdf_bytes, form_data, result):
        """Save a new report. Raises ValueError if report_id already exists."""
        with self._connect() as conn:
            if conn.execute("SELECT 1 FROM reports WHERE report_id = ?", (report_id,)).fetchone():
                raise ValueError(f"Report '{report_id}' already exists.")
            conn.execute(
                """
                INSERT INTO reports
                    (report_id, created_at, decision, credit_score,
                     biz_name, biz_type, state, loan_amount,
                     form_data_json, result_json, pdf_blob)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    datetime.now().isoformat(timespec="seconds"),
                    result.get("decision"),
                    result.get("credit_score"),
                    form_data.get("biz_name"),
                    form_data.get("biz_type"),
                    form_data.get("state"),
                    float(form_data.get("loan_amount", 0) or 0),
                    json.dumps(form_data),
                    json.dumps(result),
                    pdf_bytes,
                ),
            )

    def get_pdf(self, report_id):
        """Return raw PDF bytes, or None if not found."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT pdf_blob FROM reports WHERE report_id = ?", (report_id,)
            ).fetchone()
        return bytes(row["pdf_blob"]) if row else None

    def get_metadata(self, report_id):
        """Return all metadata (no PDF blob) as a dict, or None if not found."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT report_id, created_at, decision, credit_score,
                       biz_name, biz_type, state, loan_amount,
                       form_data_json, result_json
                FROM reports WHERE report_id = ?
                """,
                (report_id,),
            ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["form_data"] = json.loads(d.pop("form_data_json") or "{}")
        d["result"] = json.loads(d.pop("result_json") or "{}")
        return d

    def list_reports(self, limit=50):
        """Return summary rows ordered newest first."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT report_id, created_at, decision, credit_score,
                       biz_name, loan_amount
                FROM reports
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def delete_report(self, report_id):
        """Delete a report. Returns True if it existed."""
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM reports WHERE report_id = ?", (report_id,))
        return cur.rowcount > 0

    def stats(self):
        """Return aggregate stats across all reports."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*)                                                 AS total,
                    SUM(CASE WHEN decision = 'QUALIFIED' THEN 1 ELSE 0 END) AS qualified,
                    SUM(CASE WHEN decision != 'QUALIFIED' THEN 1 ELSE 0 END) AS not_qualified,
                    AVG(credit_score)                                        AS avg_score,
                    MAX(created_at)                                          AS latest
                FROM reports
                """
            ).fetchone()
        return dict(row)

    #updated_last