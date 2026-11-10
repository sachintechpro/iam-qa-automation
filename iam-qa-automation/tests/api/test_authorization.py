"""Security-oriented RBAC matrix: server must enforce least privilege.

A hidden or disabled UI button is NOT authorization. These tests directly call
backend APIs to prove unauthorized roles cannot invoke protected operations.
"""
import pytest


# Externalized test matrix: a new role/resource combination requires data, not code.
import json
from pathlib import Path
RBAC_CASES = json.loads((Path(__file__).resolve().parents[2] / 'testdata' / 'rbac_cases.json').read_text())


@pytest.mark.api
@pytest.mark.security
@pytest.mark.parametrize('case', RBAC_CASES, ids=lambda c: f"{c['role']}-{c['resource']}-{c['expected_status']}")
def test_role_permissions(api, case):
    username, route, expected = case['username'], case['resource'], case['expected_status']
    assert api.login(username).status_code == 200
    actual = api.get(route)
    assert actual.status_code == expected, f'{username} GET /api/{route}: {actual.text}'


@pytest.mark.api
@pytest.mark.security
@pytest.mark.parametrize('username,expected', [
    ('alex.viewer', 403),
    ('sam.editor', 201),
    ('jordan.admin', 201),
])
def test_write_permission(api, username, expected):
    assert api.login(username).status_code == 200
    result = api.post('projects', {'name': 'Automated QA validation'})
    assert result.status_code == expected, result.text
    if expected == 201:
        assert result.json()['name'] == 'Automated QA validation'
