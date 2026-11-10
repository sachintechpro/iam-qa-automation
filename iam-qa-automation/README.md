# IAM QA Automation Framework

**Selenium + Python + pytest + Page Object Model + REST API security + data-driven regression + GitHub Actions**

An independent, reusable QA automation showcase. The **application under test (AUT)** is [IdentityFlow](https://github.com/sachintechpro/identityflow), an educational IAM simulator. This repository contains the test framework, not the application.

> **Portfolio scope:** Real automated UI and API assertions against IdentityFlow's implemented behavior. This does **not** claim real Okta, OIDC, OAuth, TOTP, or penetration testing coverage. It uses fictional accounts only.

## What employers can evaluate

| Engineering skill | Evidence in this repository | Why it matters |
|---|---|---|
| Selenium | `tests/ui/test_login.py` | End-to-end browser actions and visible outcomes |
| Page Object Model | `framework/pages/identity_page.py` | Encapsulated selectors, semantic actions, explicit waits |
| Python architecture | `framework/api_client.py`, `conftest.py` | Reusable client and fixture separation |
| pytest | Fixtures, markers, parametrization | Maintainable suite organization and selection |
| API testing | `tests/api/test_authentication.py` | JSON status/body contracts, cookies, session state |
| Data-driven tests | `@pytest.mark.parametrize`, `testdata/rbac_cases.json` | RBAC combinations without duplicated code |
| Security validation | `tests/api/test_authorization.py`, `test_recovery.py` | 401 vs 403, lockouts, replay, MFA gating |
| Reporting | pytest-html, JUnit XML, failure screenshots | Reproducible CI evidence and triage artifacts |
| GitHub Actions | `.github/workflows/iam-tests.yml` | Automated execution, cross-repo AUT checkout, downloadable reports |

## Architecture

```text
IAM QA Automation Framework (this repository)
├── framework/api_client.py      HTTP session and JSON transport
├── framework/pages/             Selenium Page Objects
├── conftest.py                  browser/API/server fixtures + evidence capture
├── testdata/rbac_cases.json     externalized role/endpoint/expected-status matrix
├── tests/api/                   authentication, RBAC, recovery, MFA
├── tests/ui/                    real browser login and permission journeys
└── .github/workflows/           isolated CI test execution and artifacts
                 │
                 ▼
       IdentityFlow (separate GitHub repository)
       Python IAM API + HTML UI
```

## Running locally

Requires Python 3.10+, Chrome, and an extracted/cloned IdentityFlow source checkout. From the automation repository root:

```bash
python -m pip install -r requirements.txt
# Clone IdentityFlow alongside this repository:
git clone https://github.com/sachintechpro/identityflow.git ../identityflow
python -m pytest -v --html=artifacts/report.html --self-contained-html
```

By default, **each test starts a fresh temporary IdentityFlow process** on its own localhost port. This isolates lockouts, MFA enrollment, password resets, session cookies, project creation, and audit data. Local-only security tests cannot modify the public demo.

To override the AUT checkout path:

```bash
# Linux/macOS example
IAM_APP_PATH=/absolute/path/to/identityflow/identityflow python -m pytest
```

Run only the API suite:

```bash
python -m pytest -m api -v
```

Run only Selenium UI tests:

```bash
python -m pytest -m ui -v
```

Run against a **non-mutating shared demo** (local-only mutation tests automatically skip):

```bash
BASE_URL=https://identityflow.onrender.com python -m pytest -m api -v
```

For a reliable, isolated QA evaluation, run against your local source, not a live public demo (which may have changed state or gone idle).

## Example test reasoning

**Authorization is not a hidden button.** `test_role_permissions` calls protected endpoints directly to prove a Viewer receives `403` while an Admin receives `200`. An unauthenticated user receives `401`.

**Reset links must resist replay.** `test_reset_token_single_use_and_old_password_revoked` exercises a single-use reset token, rejects reuse, and confirms the old password no longer authenticates.

**UI automation must be maintainable.** `IdentityPage` owns selectors and waits. Tests describe user intentions and expected outcomes, avoiding sleeps and duplicated driver commands.

**Failure evidence matters.** When browser tests fail, a screenshot is saved; JUnit XML and an HTML report are generated on every GitHub Actions run and uploaded even if tests fail.

## Test execution notes

- CI checks out this framework and the *separate* IdentityFlow source repository, then runs isolated test servers and headless Chrome.
- CI is designed for GitHub-hosted Ubuntu runners with Chrome installed.
- Test fixtures deliberately do not print passwords, cookies, reset tokens, or MFA codes in reports.
- For future Okta/OIDC testing, add a provider-specific adapter, protected sandbox tenant, token validation tests, redirect/state/nonce assertions, and dedicated environment credentials. **None of those are implemented here.**

## Interview walkthrough (2 minutes)

1. Open the RBAC parameterized test and explain 401 vs 403 and least privilege.
2. Show the Selenium Page Object and demonstrate how a selector change affects one file rather than every test.
3. Run `python -m pytest -m api -v` and explain fixture isolation.
4. Open GitHub Actions and show the HTML/JUnit reports and automatic failure screenshots.
5. Explain why account recovery tests run against isolated local demo instances rather than shared public users.

### Important limitations

IdentityFlow is a deliberately simplified IAM simulator, not a production identity provider. These checks validate its observed contracts only; they are not a security certification or an Okta integration. The suite is a portfolio engineering demonstration, not a substitute for a formal IAM threat model or security assessment.
