"""Employer showcase: fixtures provide repeatable, isolated test environments.

Default: each test starts a fresh local IdentityFlow process. This prevents
password resets, lockouts, and MFA enrollment contaminating other tests.
BASE_URL can target an already running environment; mutating tests skip then.
"""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

from framework.api_client import IdentityApi


def _port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


@pytest.fixture
def base_url(request):
    external = os.getenv('BASE_URL')
    if external:
        if request.node.get_closest_marker('local_only'):
            pytest.skip('Mutating test disabled against shared/external target')
        yield external.rstrip('/')
        return

    app = Path(os.getenv('IAM_APP_PATH', '../identityflow/identityflow')).resolve()
    if not (app / 'app' / 'server.py').exists():
        pytest.fail(f'IdentityFlow source missing at {app}. Set IAM_APP_PATH or BASE_URL.')
    port = _port()
    env = {**os.environ, 'PORT': str(port), 'PYTHONUNBUFFERED': '1'}
    process = subprocess.Popen([sys.executable, '-m', 'app.server'], cwd=app, env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    url = f'http://127.0.0.1:{port}'
    try:
        for _ in range(100):
            if process.poll() is not None:
                pytest.fail(f'IdentityFlow exited on startup: {process.stderr.read().decode(errors="replace")[-500:]}')
            try:
                if requests.get(url + '/api/health', timeout=.25).status_code == 200:
                    break
            except requests.RequestException:
                time.sleep(.1)
        else:
            pytest.fail('IdentityFlow did not become healthy')
        yield url
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        process.stderr.close()


@pytest.fixture
def api(base_url):
    client = IdentityApi(base_url)
    yield client
    client.close()


@pytest.fixture
def driver(request):
    # Headless Chrome runs identically on a laptop and in GitHub Actions.
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--window-size=1440,1000')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    try:
        browser = webdriver.Chrome(options=opts)
    except Exception as exc:
        pytest.fail(f'Chrome/Selenium could not start: {exc}')
    yield browser
    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call' and report.failed and 'driver' in item.funcargs:
        # Attach evidence to CI artifacts without exposing passwords or cookies.
        output = Path('artifacts/screenshots')
        output.mkdir(parents=True, exist_ok=True)
        safe_name = ''.join(ch if ch.isalnum() or ch in '-_' else '_' for ch in item.nodeid)
        item.funcargs['driver'].save_screenshot(str(output / f'{safe_name}.png'))
