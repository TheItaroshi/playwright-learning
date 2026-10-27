import pytest

from playwright.sync_api import Page, expect

@pytest.fixture
def boundaries_page(page: Page, base_url: str | None) -> Page:
    origin = (base_url or "http://127.0.0.1:8000").rstrip("/")
    page.goto(f"{origin}/index.html#boundaries")
    return page


def test_iframe(boundaries_page: Page):
    bad_input = 'BAD'
    expected_input = 'LAB-2026'

    page = boundaries_page
    result_locator = page.get_by_test_id('result')

    verification_frame_locator = page.frame_locator()
    code_textbox_locator = verification_frame_locator.get_by_role('textbox')
    verification_button_locator = verification_frame_locator.get_by_role('button', name='Verify')

    code_textbox_locator.fill(bad_input)
    verification_button_locator.click()

    status_locator = verification_frame_locator.locator('#status')
    expect(status_locator).to_have_text('Invalid code')

    code_textbox_locator.clear()
    code_textbox_locator.fill(expected_input)
    verification_button_locator.click()

    expect(status_locator).to_have_text('Verification complete')
    expect(result_locator).to_have_text('Parent received: verification complete')

def test_email_notification(boundaries_page: Page):
    page = boundaries_page
    notification_locator = page.locator('lab-notifications')
    notification_switch_locator = notification_locator.get_by_role('switch', name='Email notifications')
    notification_status_locator = notification_locator.get_by_role('status')

    expect(notification_switch_locator).to_have_attribute('aria-checked', 'false')
    expect(notification_status_locator).to_have_text('Notifications off')

    notification_switch_locator.click()
    expect(notification_switch_locator).to_have_attribute('aria-checked', 'true')
    expect(notification_status_locator).to_have_text('Notifications on')

    notification_switch_locator.click()
    expect(notification_switch_locator).to_have_attribute('aria-checked', 'false')
    expect(notification_status_locator).to_have_text('Notifications off')
