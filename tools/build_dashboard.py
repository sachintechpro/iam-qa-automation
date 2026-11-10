#!/usr/bin/env python3
"""Build a public, static, privacy-conscious test results dashboard from JUnit XML.

Only test identifiers, durations and statuses are published; no raw failures,
logs, screenshots, or assertion traces are embedded in GitHub Pages.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import os
import xml.etree.ElementTree as ET

REPO = "https://github.com/sachintechpro/iam-qa-automation"
AUT = "https://identityflow.onrender.com"


def parse_junit(path):
    if not path.is_file():
        return [], "No JUnit XML was generated. Inspect the workflow run for setup errors."
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        return [], f"JUnit XML could not be read: {type(exc).__name__}."
    rows = []
    for tc in root.iter("testcase"):
        full = (tc.get("classname") or "") + "." + (tc.get("name") or "")
        name = tc.get("name") or "Unnamed test"
        marker = next((k for k in ("error", "failure", "skipped") if tc.find(k) is not None), None)
        status = {None:"PASSED", "error":"ERROR", "failure":"FAILED", "skipped":"SKIPPED"}[marker]
        kind = "UI · Selenium" if "tests.ui" in full or "/ui/" in full or "test_login" in full else "API · Requests"
        try:
            duration = max(0.0, float(tc.get("time") or "0"))
        except ValueError:
            duration = 0.0
        rows.append((name, kind, status, duration))
    return rows, None


def render(rows, problem=None):
    counts = Counter(r[2] for r in rows)
    passed = counts["PASSED"]
    total = len(rows)
    failures = counts["FAILED"] + counts["ERROR"]
    state = "PASSED" if total and not failures and not problem else "FAILED" if failures else "INCOMPLETE"
    ui = [r for r in rows if r[1].startswith("UI")]
    api = [r for r in rows if r[1].startswith("API")]
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    slug = os.environ.get("GITHUB_REPOSITORY", "sachintechpro/iam-qa-automation")
    run_url = f"{server}/{slug}/actions/runs/{run_id}" if run_id else f"{REPO}/actions"
    sha = os.environ.get("GITHUB_SHA", "")[:8] or "—"
    at = datetime.now(timezone.utc).strftime("%b %d, %Y · %H:%M UTC")
    lines = "".join(
        f'<tr><td><span class="test-name">{escape(name)}</span></td><td>{escape(kind)}</td>'
        f'<td><span class="pill {status.lower()}">{status}</span></td><td class="number">{secs:.2f}s</td></tr>'
        for name, kind, status, secs in sorted(rows, key=lambda r: (r[1], r[0]))
    ) or '<tr><td colspan="4">No test cases available for this execution.</td></tr>'
    warning = f'<div class="note warning">{escape(problem)}</div>' if problem else ''
    status_color = {"PASSED":"#16734c", "FAILED":"#ac3440", "INCOMPLETE":"#956213"}[state]
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Latest IAM QA Automation results from GitHub Actions: Python, pytest, Selenium, and API regression tests.">
<title>IAM QA Automation — Latest Test Results</title>
<style>
:root{{--ink:#182438;--muted:#66768b;--border:#e3e8ef;--bg:#f7f9fc;--blue:#2059bb}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}
a{{color:var(--blue);text-decoration:none}}a:hover{{text-decoration:underline}}.shell{{max-width:1120px;margin:0 auto;padding:0 26px}}
header{{background:white;border-bottom:1px solid var(--border)}}header .shell{{display:flex;justify-content:space-between;gap:16px;align-items:center;padding-top:18px;padding-bottom:18px}}.brand{{font-weight:800;font-size:18px;letter-spacing:-.4px}}.brand b{{color:var(--blue)}}
.links{{display:flex;flex-wrap:wrap;gap:18px;font-size:13px}}main{{padding:48px 0 60px}}.kicker{{font-size:11px;color:var(--blue);font-weight:800;letter-spacing:1.5px}}h1{{font-size:clamp(30px,5vw,44px);margin:8px 0;letter-spacing:-1.5px}}.intro{{color:var(--muted);max-width:720px}}
.header-row{{display:flex;align-items:center;flex-wrap:wrap;gap:14px}}.status{{padding:5px 11px;background:#fff;border:1px solid {status_color};color:{status_color};border-radius:6px;font-weight:800;font-size:12px}}
.cards{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:28px 0}}.card{{background:white;border:1px solid var(--border);border-radius:12px;padding:19px}}.card label{{font-size:12px;color:var(--muted);display:block}}.card strong{{font-size:29px;display:block;letter-spacing:-1px;margin-top:6px}}
.panel{{background:white;border:1px solid var(--border);border-radius:12px;overflow:hidden}}.panel-head{{padding:23px;border-bottom:1px solid var(--border)}}.panel-head h2{{margin:0;font-size:19px}}.panel-head p{{color:var(--muted);font-size:12px;margin:5px 0 0}}table{{width:100%;border-collapse:collapse;text-align:left}}th,td{{padding:12px 18px;border-bottom:1px solid #edf0f4;font-size:13px}}th{{font-size:11px;letter-spacing:.5px;color:var(--muted);background:#fafbfd}}.test-name{{overflow-wrap:anywhere}}.number{{white-space:nowrap;text-align:right}}.pill{{font-size:10px;font-weight:800;border-radius:4px;padding:4px 7px}}.passed{{background:#e6f7ee;color:#166441}}.failed,.error{{background:#fce8e9;color:#a02c35}}.skipped{{background:#fff3da;color:#815912}}
.note{{border:1px solid #dae3ef;background:#eff5ff;padding:16px 18px;border-radius:9px;font-size:13px;color:#486079;margin:20px 0}}.warning{{background:#fff6e6;color:#76551f;border-color:#f1dfbb}}.meta{{display:flex;flex-wrap:wrap;gap:18px;font-size:12px;color:var(--muted)}}footer{{padding:0 0 35px;font-size:12px;color:var(--muted)}}
@media(max-width:650px){{.cards{{grid-template-columns:repeat(2,minmax(0,1fr))}}header .shell{{display:block}}.links{{margin-top:10px}}th,td{{padding:10px 9px}}}}
</style></head><body>
<header><div class="shell"><span class="brand">IAM <b>QA Automation</b></span><nav class="links"><a href="{REPO}">Source code</a><a href="{AUT}">Live IAM app</a><a href="{escape(run_url, quote=True)}">GitHub Actions run</a></nav></div></header>
<main class="shell"><div class="kicker">AUTOMATED TEST EXECUTION</div><div class="header-row"><h1>Latest test results</h1><span class="status">{state}</span></div>
<p class="intro">Results generated from pytest JUnit XML by GitHub Actions. The suite tests an isolated local checkout of IdentityFlow; it does not run destructive tests against the public demo.</p>
<div class="meta"><span>Updated: {at}</span><span>Commit: {escape(sha)}</span><span><a href="{escape(run_url, quote=True)}">View exact workflow execution</a></span></div>
<div class="cards"><div class="card"><label>Total tests</label><strong>{total}</strong></div><div class="card"><label>Passed</label><strong>{passed}</strong></div><div class="card"><label>API tests passed</label><strong>{sum(r[2]=='PASSED' for r in api)}/{len(api)}</strong></div><div class="card"><label>Selenium UI passed</label><strong>{sum(r[2]=='PASSED' for r in ui)}/{len(ui)}</strong></div></div>
{warning}
<div class="panel"><div class="panel-head"><h2>Execution details</h2><p>Individual test outcomes; failure traces, credentials, and screenshots are not published to this public site.</p></div><div style="overflow-x:auto"><table><thead><tr><th>Test case</th><th>Layer</th><th>Status</th><th class="number">Duration</th></tr></thead><tbody>{lines}</tbody></table></div></div>
<div class="note">For full pytest HTML reports, JUnit XML and failure screenshots, open the <a href="{escape(run_url, quote=True)}">GitHub Actions run</a> and download its <strong>iam-qa-test-results</strong> artifact. Artifacts may expire under repository retention settings.</div>
</main><footer class="shell">Fictional IAM simulator · Public reporting excludes stack traces and sensitive runtime evidence.</footer></body></html>'''


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--junit", default="iam-qa-automation/reports/results.xml")
    p.add_argument("--out", default="site/index.html")
    args = p.parse_args()
    rows, problem = parse_junit(Path(args.junit))
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(rows, problem), encoding="utf-8")
    print(f"Dashboard generated: {target} ({len(rows)} tests)")

if __name__ == "__main__":
    main()
