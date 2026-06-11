#!/usr/bin/env python3
"""
Career-Ops Hermes — Standalone Web Dashboard Server
Zero dependencies (Python stdlib only).

Serves:
  /           Dashboard HTML
  /api/tracker        Tracker data (from data/applications.md)
  /api/pipeline       Pipeline data (from data/pipeline.md)
  /api/reports        List all reports
  /api/report/<name>  Read a report
  /api/report-by-num/<num>  Read report by tracker number
  /api/scan-status    Scanner config summary
  /api/stats          Aggregate statistics
  /api/process        Trigger pipeline processing (POST)

Run:
  python3 dashboard-server.py [--port PORT] [--project-dir PATH]
"""

import http.server
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler with JSON API endpoints."""

    # Set by main()
    project_dir: Path = None
    html_path: Path = None

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, content, status=200):
        body = content.encode("utf-8") if isinstance(content, str) else content
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error(self, msg, status=404):
        self._json({"error": msg}, status)

    def _safe_read(self, path, default=""):
        """Read a file, return default if not found."""
        try:
            return Path(path).read_text()
        except Exception:
            return default

    def _parse_applications(self):
        """Parse data/applications.md into rows."""
        tracker_path = self.project_dir / "data" / "applications.md"
        content = self._safe_read(tracker_path)
        if not content:
            return []

        rows = []
        in_table = False
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("| #") and "Date" in line:
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")]
                parts = [p for p in parts if p]  # remove empty from leading/trailing |
                if len(parts) >= 6:
                    try:
                        num = parts[0] if parts[0].isdigit() else 0
                        rows.append({
                            "num": num,
                            "date": parts[1],
                            "company": parts[2],
                            "role": parts[3],
                            "score": parts[4],
                            "status": parts[5],
                            "pdf": parts[6] if len(parts) > 6 else "",
                            "report": parts[7] if len(parts) > 7 else "",
                            "notes": parts[8] if len(parts) > 8 else "",
                        })
                    except (IndexError, ValueError):
                        continue
            elif in_table and not line.startswith("|"):
                break
        return rows

    def _parse_pipeline(self):
        """Parse data/pipeline.md into pending and processed lists."""
        pipeline_path = self.project_dir / "data" / "pipeline.md"
        content = self._safe_read(pipeline_path)
        pending = []
        processed = []

        section = None
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("## Pending") or stripped.startswith("## Pendiente"):
                section = "pending"
                continue
            if stripped.startswith("## Processed") or stripped.startswith("## Procesad"):
                section = "processed"
                continue
            if stripped.startswith("##"):
                section = None
                continue

            if section == "pending" and stripped.startswith("- ["):
                # - [ ] URL | Company | Title
                m = re.match(r'-\s*\[\s*([! x])\s*\]\s*(.+)', stripped)
                if m:
                    status_mark = m.group(1)
                    rest = m.group(2)
                    parts = [p.strip() for p in rest.split("|")]
                    entry = {
                        "url": parts[0] if parts else "",
                        "company": parts[1] if len(parts) > 1 else "",
                        "title": parts[2] if len(parts) > 2 else "",
                        "status": "error" if status_mark == "!" else "pending",
                    }
                    pending.append(entry)

            if section == "processed" and stripped.startswith("- [x]"):
                m = re.match(r'-\s*\[\s*x\s*\]\s*(.+)', stripped)
                if m:
                    rest = m.group(1)
                    parts = [p.strip() for p in rest.split("|")]
                    processed.append({
                        "line": rest,
                        "num": parts[0] if parts else "",
                        "company": parts[2] if len(parts) > 2 else "",
                        "title": parts[3] if len(parts) > 3 else "",
                        "score": parts[4] if len(parts) > 4 else "",
                    })

        return {"pending": pending, "processed": processed}

    def _list_reports(self):
        """List reports in reports/ directory."""
        reports_dir = self.project_dir / "reports"
        if not reports_dir.exists():
            return []

        reports = []
        for f in sorted(reports_dir.glob("*.md"), reverse=True):
            filename = f.name
            # Parse: {num}-{company-slug}-{date}.md
            m = re.match(r'^(\d+)-(.+)-(\d{4}-\d{2}-\d{2})\.md$', filename)
            if m:
                # Read first 10 lines for metadata
                head = ""
                try:
                    with open(f) as fh:
                        for i, line in enumerate(fh):
                            if i >= 10:
                                break
                            head += line
                except Exception:
                    pass

                score = ""
                score_m = re.search(r'\*\*Score:\*\*\s*([\d.]+)/5', head)
                if score_m:
                    score = score_m.group(1)

                reports.append({
                    "filename": filename,
                    "num": int(m.group(1)),
                    "slug": m.group(2),
                    "date": m.group(3),
                    "company": m.group(2).replace("-", " ").title(),
                    "role": "",
                    "score": score,
                })
        return reports

    def _scan_status(self):
        """Get scanner configuration summary."""
        portals_path = self.project_dir / "portals.yml"
        companies = 0
        queries = 0
        if portals_path.exists():
            try:
                content = portals_path.read_text()
                companies = content.count("name:")
                queries = content.count("query:")
            except Exception:
                pass

        # Count scan history
        history_path = self.project_dir / "data" / "scan-history.tsv"
        scans = 0
        if history_path.exists():
            try:
                scans = len(history_path.read_text().strip().split("\n")) - 1
            except Exception:
                pass

        return {"companies": companies, "queries": queries, "scans": max(0, scans)}

    # ── Routes ──

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        # Root — serve dashboard HTML
        if path == "" or path == "/":
            try:
                html = self.html_path.read_bytes()
                self._html(html)
            except FileNotFoundError:
                self._error("Dashboard not found", 500)
            return

        # API: tracker
        if path == "/api/tracker":
            rows = self._parse_applications()
            stats = {
                "total": len(rows),
                "applied": sum(1 for r in rows if r["status"] in ("Applied", "Responded", "Interview", "Offer")),
                "interview": sum(1 for r in rows if r["status"] == "Interview"),
                "offer": sum(1 for r in rows if r["status"] == "Offer"),
                "avg_score": 0,
                "by_status": {},
            }
            scores = []
            for r in rows:
                try:
                    s = float(re.sub(r'[^\d.]', '', str(r["score"])))
                    scores.append(s)
                except (ValueError, TypeError):
                    pass
                stats["by_status"][r["status"]] = stats["by_status"].get(r["status"], 0) + 1
            if scores:
                stats["avg_score"] = round(sum(scores) / len(scores), 1)
            self._json({"rows": rows, "stats": stats})
            return

        # API: pipeline
        if path == "/api/pipeline":
            data = self._parse_pipeline()
            self._json(data)
            return

        # API: reports list
        if path == "/api/reports":
            reports = self._list_reports()
            self._json(reports)
            return

        # API: single report by filename
        if path.startswith("/api/report/"):
            filename = path.split("/api/report/", 1)[1]
            # Sanitize: only allow .md files
            if ".." in filename or "/" in filename or not filename.endswith(".md"):
                self._error("Invalid filename", 400)
                return
            report_path = self.project_dir / "reports" / filename
            try:
                content = report_path.read_text()
                self._json({"filename": filename, "content": content})
            except FileNotFoundError:
                self._error("Report not found")
            return

        # API: report by tracker number
        if path.startswith("/api/report-by-num/"):
            try:
                num = int(path.split("/api/report-by-num/", 1)[1])
            except ValueError:
                self._error("Invalid number", 400)
                return

            # Find the report file by number prefix
            reports_dir = self.project_dir / "reports"
            found = None
            if reports_dir.exists():
                for f in reports_dir.glob(f"{num:03d}-*.md"):
                    found = f
                    break
            if found:
                content = found.read_text()
                self._json({"filename": found.name, "content": content})
            else:
                self._error(f"Report #{num:03d} not found")
            return

        # API: scan status
        if path == "/api/scan-status":
            self._json(self._scan_status())
            return

        # API: stats
        if path == "/api/stats":
            rows = self._parse_applications()
            pipeline = self._parse_pipeline()
            reports = self._list_reports()
            self._json({
                "applications": len(rows),
                "pipeline_pending": len(pipeline["pending"]),
                "pipeline_processed": len(pipeline["processed"]),
                "reports": len(reports),
                "scan": self._scan_status(),
            })
            return

        # 404
        self._error(f"Not found: {path}")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/api/process":
            # Trigger pipeline processing (async)
            self._json({"status": "accepted", "message": "Pipeline processing triggered"})
            # Could spawn background process here
            return

        self._error("Not found", 404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """Quiet logging."""
        if args[1] != "200":  # Only log non-200
            sys.stderr.write(f"[dashboard] {args[0]} {format % args}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Career-Ops Hermes Dashboard Server")
    parser.add_argument("--port", type=int, default=8790, help="Server port (default: 8790)")
    parser.add_argument(
        "--project-dir",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="Career-Ops project directory",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    html_path = project_dir / "webui" / "index.html"

    if not html_path.exists():
        print(f"ERROR: Dashboard HTML not found at {html_path}", file=sys.stderr)
        sys.exit(1)

    DashboardHandler.project_dir = project_dir
    DashboardHandler.html_path = html_path

    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), DashboardHandler)
    print(f"🎯 Career-Ops Hermes Dashboard")
    print(f"   URL:        http://127.0.0.1:{args.port}")
    print(f"   Project:    {project_dir}")
    print(f"   State dir:  {project_dir / 'data'}")
    print(f"   Press Ctrl+C to stop")
    sys.stdout.flush()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
