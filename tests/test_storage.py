import pytest

from playwright.sync_api import Page, expect, Browser

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

def test_separate_context(storage_page: Page, browser: Browser):
    email = 'learner@example.com'
    password = 'practice123'

    page = storage_page
    email_textbox_locator = page.get_by_label('Email')
    password_textbox_locator = page.get_by_label('Password')
    account_theme_locator = page.get_by_label('Saved accent preference')
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
    account_theme_locator.select_option('Ocean')

    context_b = browser.new_context()
    try:
        page_b = context_b.new_page()
        page_b.goto(storage_page.url)

        page_b_email_textbox_locator = page_b.get_by_label('Email')
        page_b_password_textbox_locator = page_b.get_by_label('Password')
        page_b_account_theme_locator = page_b.get_by_label('Saved accent preference')
        page_b_sign_in_button_locator = page_b.get_by_role('button', name='Sign in')

        expect(page_b_email_textbox_locator).to_be_visible()
        expect(page_b_password_textbox_locator).to_be_visible()
        expect(page_b_account_theme_locator).to_be_visible()
        expect(page_b_sign_in_button_locator).to_be_visible()

        expect(page_b_account_theme_locator).to_have_value('Sage')
        expect(account_theme_locator).to_have_value('Ocean')
    finally:
        context_b.close()

    expect(result_locator).to_contain_text(f'Signed in as {email}')
    expect(sign_out_button_locator).to_be_visible()

def test_load_context(storage_page: Page, browser: Browser, tmp_path):
    email = 'learner@example.com'
    password = 'practice123'

    page = storage_page
    email_textbox_locator = page.get_by_label('Email')
    password_textbox_locator = page.get_by_label('Password')
    account_theme_locator = page.get_by_label('Saved accent preference')
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
    account_theme_locator.select_option('Ocean')

    expect(result_locator).to_contain_text(f'Signed in as {email}')
    expect(sign_out_button_locator).to_be_visible()

    context_path = tmp_path / 'context.json'
    page.context.storage_state(path=context_path)

    context_c = browser.new_context(storage_state=context_path)
    try:
        page_c = context_c.new_page()
        page_c.goto(storage_page.url)

        page_c_email_textbox_locator = page_c.get_by_label('Email')
        page_c_password_textbox_locator = page_c.get_by_label('Password')
        page_c_account_theme_locator = page_c.get_by_label('Saved accent preference')
        page_c_sign_in_button_locator = page_c.get_by_role('button', name='Sign in')

        expect(page_c_email_textbox_locator).to_be_visible()
        expect(page_c_password_textbox_locator).to_be_visible()
        expect(page_c_account_theme_locator).to_be_visible()
        expect(page_c_sign_in_button_locator).to_be_visible()

        expect(page_c_account_theme_locator).to_have_value('Ocean')
    finally:
        context_c.close()

def test_incorrect_password(storage_page: Page):
    email = 'learner@example.com'
    password = 'wrong_password'

    page = storage_page
    email_textbox_locator = page.get_by_label('Email')
    password_textbox_locator = page.get_by_label('Password')
    sign_in_button_locator = page.get_by_role('button', name='Sign in')
    result_locator = page.get_by_test_id('result')

    email_textbox_locator.fill(email)
    password_textbox_locator.fill(password)
    sign_in_button_locator.click()

    expect(email_textbox_locator).to_be_visible()
    expect(password_textbox_locator).to_be_visible()
    expect(sign_in_button_locator).to_be_visible()
    expect(result_locator).to_have_text('Incorrect email or password')
