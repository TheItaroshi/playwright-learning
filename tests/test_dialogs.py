import pytest

from playwright.sync_api import Page, expect

@pytest.fixture
def dialogs_page(page: Page, base_url: str | None) -> Page:
    origin = (base_url or "http://127.0.0.1:8000").rstrip("/")
    page.goto(f"{origin}/index.html#dialogs")
    return page

def handle_dialog(dialog, accept:bool):
    if accept:
        dialog.accept()
    else:
        dialog.dismiss()

def test_alert_dialog(dialogs_page: Page):
    page = dialogs_page
    alert_button_locator = page.locator('#alert')
    result_locator = page.get_by_test_id('result')

    page.once('dialog', lambda dialog:handle_dialog(dialog, True))
    alert_button_locator.click()

    expect(result_locator).to_contain_text('Alert acknowledged')

def test_confirm_dialog_accept(dialogs_page: Page):
    page = dialogs_page
    alert_button_locator = page.locator('#confirm')
    result_locator = page.get_by_test_id('result')

    page.once('dialog', lambda dialog:handle_dialog(dialog, True))
    alert_button_locator.click()

    expect(result_locator).to_contain_text('Action confirmed')

def test_confirm_dialog_dismiss(dialogs_page: Page):
    page = dialogs_page
    alert_button_locator = page.locator('#confirm')
    result_locator = page.get_by_test_id('result')

    page.once('dialog', lambda dialog:handle_dialog(dialog, False))
    alert_button_locator.click()

    expect(result_locator).to_contain_text('Action cancelled')
