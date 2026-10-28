import pytest

from playwright.sync_api import Page, expect, Locator, Playwright

@pytest.fixture
def storage_page(page: Page, base_url: str | None) -> Page:
    origin = (base_url or "http://127.0.0.1:8000").rstrip("/")
    page.goto(f"{origin}/index.html#storage")
    return page

def test_session_lifetime(storage_page: Page):
    email = 'learner@example.com'
    password = 'practice123'

    page = storage_page
    email_textbox_locator = page.get_by_label('Email')
    password_textbox_locator = page.get_by_label('Password')
    sign_in_button_locator = page.get_by_role('button', name='Sign in')

    email_textbox_locator.fill(email)
    password_textbox_locator.fill(password)
    sign_in_button_locator.click()

    result_locator = page.locator('.result').first
    expect(result_locator).to_contain_text(f'Signed in as {email}')
    expect(email_textbox_locator).to_be_hidden()
    expect(password_textbox_locator).to_be_hidden()
    expect(sign_in_button_locator).to_be_hidden()

    sign_out_button_locator = page.get_by_role('button', name='Sign out')

    page.reload()
    expect(result_locator).to_contain_text(f'Signed in as {email}')
    expect(sign_out_button_locator).to_be_visible()
    sign_out_button_locator.click()

    expect(email_textbox_locator).to_be_visible()
    expect(password_textbox_locator).to_be_visible()
    expect(sign_in_button_locator).to_be_visible()
