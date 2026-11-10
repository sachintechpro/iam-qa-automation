Enterprise IAM QA Automation Framework
![IAM QA Automation Tests](https://github.com/sachintechpro/iam-qa-automation/actions/workflows/qa-tests.yml)
Selenium WebDriver · Python · pytest · Page Object Model · REST API · Data-driven RBAC · Security Regression · HTML/JUnit Reporting · GitHub Actions
View successful CI run (21/21 passed) · Live application under test · IdentityFlow source
An independently maintained, automated IAM test framework targeting the fictional IdentityFlow authentication simulator. It exercises the application's actual web UI and HTTP endpoints, with a focus on maintainable architecture, reproducible test data, negative security paths and actionable test evidence.
> \*\*Verified CI baseline:\*\* 21 tests passed in 17.00 seconds on GitHub Actions run #3 (commit `4d3e4b8`): \*\*19 API tests and 2 headless Selenium UI tests\*\*. The green badge reflects future runs and may change when the code changes. The application under test is a simulator, \*\*not\*\* real Okta, OAuth/OIDC, TOTP or a production identity provider.
What to look at first (employer walkthrough)
Engineering capability	Evidence	Design decision being demonstrated
Selenium WebDriver	`tests/ui/test\_login.py`	Real Chrome browser journeys for login and authorization; assert actual HTTP outcomes in UI
Page Object Model	`framework/pages/identity\_page.py`	One place for selectors, user actions and explicit waits; avoids duplication and hard-coded sleeps
Python / pytest	`conftest.py`	Reusable fixtures start an isolated app process per test and clean it up afterward
API regression	`framework/api\_client.py`	`requests.Session` maintains cookies inside a test, without leaking state between cases
Data-driven testing	`testdata/rbac\_cases.json`	RBAC cases are data, not repetitive conditional code
IAM negative tests	`tests/api/`	Check unauthenticated (401) versus authenticated-but-forbidden (403), reset token reuse, lockouts and MFA gates
Automated evidence	CI workflow	HTML test report and JUnit XML available as downloadable artifacts, even on failures
Verified execution
Layer	Cases	Result
API tests: authentication, permissions, recovery and MFA	19	Passed
Selenium UI: Viewer denied project creation, Editor permitted	2	Passed
Total	21	Passed
Inspect the exact green GitHub Actions run (the run records the tested commit, logs and archived reports). No security certification or broad penetration-testing claim is implied.
Download and inspect a test report
Open the successful workflow run.
Scroll to Artifacts and download `iam-qa-test-results`.
Unzip it. Open `report.html` in a browser to inspect pytest-html results, or load `results.xml` into a JUnit-compatible viewer.
On a failed UI test, inspect captured screenshots if available; these are produced by the failure hook. Reports and screenshots are CI evidence, not manually curated success images.
Framework architecture
```text
GitHub Actions (qa-tests.yml)
    ├── checkout this test framework
    ├── checkout IdentityFlow (separate AUT repository)
    ├── install Python + pytest + Selenium dependencies
    └── run pytest against isolated local IdentityFlow processes
               │
        conftest.py fixtures
        ├── temporary port + fresh AUT process per test
        ├── API client with scoped cookie session
        └── headless Chrome driver + failure screenshot hook
               │
          ┌────┴─────┐
          ▼          ▼
       API tests   UI tests
       requests    Selenium WebDriver
       RBAC data   Page Object Model
          └────┬─────┘
               ▼
       IdentityFlow API + UI
               │
               ▼
         pytest-html / JUnit XML
         GitHub Actions artifacts
```
The application is not hosted by this repository. The test suite starts a fresh local copy of IdentityFlow for each test by default, rather than mutating shared public demo accounts.
Run locally
Requirements: Python 3.10+, Google Chrome, and Git. The commands below assume both repositories are cloned into sibling folders.
```bash
git clone https://github.com/sachintechpro/identityflow.git
git clone https://github.com/sachintechpro/iam-qa-automation.git
cd iam-qa-automation/iam-qa-automation
python -m pip install -r requirements.txt
IAM\_APP\_PATH="$(cd ../../identityflow/identityflow \&\& pwd)" python -m pytest -v --html=reports/report.html --self-contained-html --junitxml=reports/results.xml
```
The command above explicitly points `IAM\_APP\_PATH` at the checked-out IdentityFlow app directory. This avoids assumptions about sibling-folder layouts. Set `IAM\_APP\_PATH` separately when running focused suites below, or use the PowerShell example on Windows. Chrome is used headlessly for UI tests.
Run focused suites:
```bash
python -m pytest -m api -v
python -m pytest -m ui -v
python -m pytest -m security -v
```
For Windows PowerShell with a different checkout location:
```powershell
$env:IAM\_APP\_PATH = "C:\\path\\to\\identityflow\\identityflow"
python -m pytest -v
```
Test-design decisions worth discussing
Authorization requires backend assertions. A hidden or disabled button is not a security boundary. API tests exercise protected endpoints directly and distinguish `401` (no valid session) from `403` (logged in but insufficient privileges).
Stateful IAM scenarios need isolation. Password resets, account lockouts, MFA enrollment and new projects would contaminate subsequent tests if they shared an account. The pytest fixtures start and stop a fresh IdentityFlow process per test case.
The Page Object owns the browser mechanics. Selectors and explicit waits live in `IdentityPage`, while test functions read as business journeys. A real CI issue was resolved by changing Selenium from `select\_by\_value()` to `select\_by\_visible\_text()` to match the AUT's dropdown HTML.
Data-driven coverage avoids repetitive test code. A JSON RBAC matrix separates expected access policies from test execution logic, making permission changes visible in code review.
Failed pipelines are useful evidence. Initial CI runs exposed an incorrect `IAM\_APP\_PATH` environment variable and then a Selenium selector mismatch. Both were fixed, and run #3 passed all 21 tests.
Scope and limitations
The AUT is a purposely simplified educational simulator with fictional demo users. Do not use real credentials or customer data.
This framework does not implement Okta integration, real SSO/OIDC token validation, authenticator-app TOTP, password spraying, or a full penetration-testing methodology.
The two Selenium scenarios prove a small set of browser journeys; extensive page-flow, accessibility and cross-browser coverage remain future opportunities.
The latest hosted demo UI can differ from the version checked out by CI. The CI run is the reproducible test evidence; the hosted link is for hands-on exploration, not the target of destructive security tests.
Suggested 2-minute interview walkthrough
Open the green GitHub Actions run and show the 21 passed result and downloadable HTML report.
Open `IdentityPage` and explain your Selenium Page Object Model and explicit waits.
Show `testdata/rbac\_cases.json` and one parameterized authorization test: explain `401` versus `403`.
Open `conftest.py` and describe test isolation and why shared IAM accounts create flaky tests.
Explain the CI debugging path: path configuration first, then a dropdown locator mismatch, followed by a clean green run.
This repository demonstrates QA automation design and execution, not just a list of test-case titles.
