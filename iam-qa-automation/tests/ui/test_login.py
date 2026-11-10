"""UI journey tests verify the user experience, complementing API authorization tests."""
import pytest
from framework.pages.identity_page import IdentityPage


@pytest.mark.ui
def test_viewer_login_and_denied_create(driver, base_url):
    page = IdentityPage(driver, base_url).open().login('alex.viewer', 'DemoPass!2026')
    assert 'HTTP 200' in page.session_text()
    # The browser must reflect the backend's real 403; UI visibility is irrelevant.
    assert 'HTTP 403' in page.create_project('Should not be created')


@pytest.mark.ui
def test_editor_can_create_project(driver, base_url):
    page = IdentityPage(driver, base_url).open().login('sam.editor', 'DemoPass!2026')
    assert 'HTTP 200' in page.session_text()
    assert 'HTTP 201' in page.create_project('Automation showcase')
    page.logout()
    assert 'HTTP 200' in page.session_text()
