"""Authentication contract testing: assert both HTTP semantics and response content."""
import pytest


@pytest.mark.api
@pytest.mark.parametrize('username,password,expected', [
    pytest.param('alex.viewer', 'DemoPass!2026', 200, id='valid-viewer'),
    pytest.param('alex.viewer', 'incorrect-password', 401, id='wrong-password'),
    pytest.param('does.not.exist', 'DemoPass!2026', 401, id='unknown-username'),
])
def test_login_data_driven(api, username, password, expected):
    # Employer showcase: parametrization avoids copy/paste test scripts.
    response = api.login(username, password)
    assert response.status_code == expected, response.text
    if expected == 200:
        assert response.json()['role'] == 'viewer'
    else:
        assert 'error' in response.json()


@pytest.mark.api
@pytest.mark.security
def test_protected_endpoint_without_session(api):
    response = api.get('projects')
    assert response.status_code == 401


@pytest.mark.api
@pytest.mark.security
def test_logout_revokes_session(api):
    assert api.login().status_code == 200
    assert api.get('me').status_code == 200
    assert api.post('logout', {}).status_code == 200
    assert api.get('me').status_code == 401


@pytest.mark.api
@pytest.mark.security
def test_post_requires_custom_demo_header(base_url):
    # API negative test: bypass the framework's usual request header on purpose.
    import requests
    response = requests.post(base_url + '/api/login',
                             json={'username': 'alex.viewer', 'password': 'DemoPass!2026'}, timeout=15)
    assert response.status_code == 403
