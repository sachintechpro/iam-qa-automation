"""State-changing security scenarios run only against fresh local simulator instances."""
import pytest


@pytest.mark.api
@pytest.mark.security
@pytest.mark.local_only
def test_reset_token_single_use_and_old_password_revoked(api):
    token_reply = api.post('request-reset', {'email': 'alex.viewer@example.test'})
    assert token_reply.status_code == 200
    token = token_reply.json()['demo_token']
    assert token  # Exposed for educational simulator ONLY.
    changed = api.post('reset-password', {'token': token, 'password': 'ChangedDemo!2027'})
    assert changed.status_code == 200
    assert api.post('reset-password', {'token': token, 'password': 'ChangedAgain!2028'}).status_code == 400
    assert api.login(password='DemoPass!2026').status_code == 401
    assert api.login(password='ChangedDemo!2027').status_code == 200


@pytest.mark.api
@pytest.mark.security
@pytest.mark.local_only
def test_five_bad_passwords_lock_account(api):
    statuses = [api.login(password='wrong').status_code for _ in range(5)]
    assert statuses[:4] == [401] * 4
    assert statuses[4] == 423
    assert api.login().status_code == 423


@pytest.mark.api
@pytest.mark.security
@pytest.mark.local_only
def test_mfa_challenge_is_required_after_enrollment(api):
    assert api.login().status_code == 200
    enrolled = api.post('mfa/enroll', {})
    assert enrolled.status_code == 200
    api.post('logout', {})
    login = api.login()
    assert login.status_code == 200
    payload = login.json()
    assert payload['mfa_required'] is True
    assert api.get('me').status_code == 401
    assert api.post('mfa/verify', {'challenge': payload['challenge'], 'code': 'not-a-code'}).status_code == 401
    assert api.post('mfa/verify', {'challenge': payload['challenge'], 'code': payload['demo_code']}).status_code == 200
    assert api.get('me').status_code == 200
