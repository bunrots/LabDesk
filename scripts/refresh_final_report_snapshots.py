from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from labdesk import create_app
from labdesk.db import get_db
from labdesk.services import get_report_bundle, render_snapshot_html


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh stored HTML snapshots for finalized reports using the current print template."
    )
    parser.add_argument(
        "--report-id",
        type=int,
        action="append",
        help="Refresh only the specified finalized report ID. Repeat to target multiple reports.",
    )
    args = parser.parse_args()

    app = create_app({"DEBUG": False})
    refreshed = 0

    with app.app_context():
        db = get_db()
        if args.report_id:
            placeholders = ",".join("?" for _ in args.report_id)
            rows = db.execute(
                f"SELECT id FROM reports WHERE status = 'final' AND id IN ({placeholders}) ORDER BY id",
                tuple(args.report_id),
            ).fetchall()
        else:
            rows = db.execute("SELECT id FROM reports WHERE status = 'final' ORDER BY id").fetchall()

        for row in rows:
            report_id = row["id"]
            bundle = get_report_bundle(db, report_id)
            if bundle is None:
                continue
            with app.test_request_context("/"):
                snapshot_html = render_snapshot_html(bundle)
            db.execute(
                """
                UPDATE reports
                SET snapshot_html = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (snapshot_html, report_id),
            )
            refreshed += 1

        db.commit()

    print(f"Refreshed {refreshed} finalized report snapshot(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
