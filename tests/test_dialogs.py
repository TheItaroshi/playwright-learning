import pytest

from playwright.sync_api import Page, expect, Dialog

@pytest.fixture
def dialogs_page(page: Page, base_url: str | None) -> Page:
    origin = (base_url or "http://127.0.0.1:8000").rstrip("/")
    page.goto(f"{origin}/index.html#dialogs")
    return page

def handle_dialog(dialog, accept:bool, prompt_string:str = ''):
    if accept:
        if dialog.type == 'prompt':
            dialog.accept(prompt_string)
        else:
            dialog.accept()
    elif not accept:
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
    confirm_button_locator = page.locator('#confirm')
    result_locator = page.get_by_test_id('result')

    page.once('dialog', lambda dialog:handle_dialog(dialog, True))
    confirm_button_locator.click()

    expect(result_locator).to_contain_text('Action confirmed')

def test_confirm_dialog_dismiss(dialogs_page: Page):
    page = dialogs_page
    confirm_button_locator = page.locator('#confirm')
    result_locator = page.get_by_test_id('result')

    page.once('dialog', lambda dialog:handle_dialog(dialog, False))
    confirm_button_locator.click()

    expect(result_locator).to_contain_text('Action cancelled')

def test_prompt_dialog_accept(dialogs_page: Page):
    page = dialogs_page
    prompt_button_locator = page.locator('#prompt')
    result_locator = page.get_by_test_id('result')
    name = 'Ada'

    page.once('dialog', lambda dialog:handle_dialog(dialog, True, prompt_string=name))
    prompt_button_locator.click()

    expect(result_locator).to_contain_text(f'Hello, {name}!')

def test_prompt_dialog_dismiss(dialogs_page: Page):
    page = dialogs_page
    prompt_button_locator = page.locator('#prompt')
    result_locator = page.get_by_test_id('result')

    page.once('dialog', lambda dialog:handle_dialog(dialog, False))
    prompt_button_locator.click()

    expect(result_locator).to_contain_text('Prompt cancelled')

def test_create_project(dialogs_page: Page):
    page = dialogs_page
    project_button_locator = page.locator('#open-modal')
    result_locator = page.get_by_test_id('result')
    project_dialog_locator = page.get_by_role('dialog', name='Create project')
    project_input = project_dialog_locator.get_by_role('textbox')
    project_save_locator = project_dialog_locator.get_by_role('button', name='Save project')
    project_name = 'Regression suite'

    expect(project_button_locator).to_be_visible()
    project_button_locator.click()

    expect(project_dialog_locator).to_be_visible()
    project_input.fill(project_name)
    project_save_locator.click()

    expect(project_dialog_locator).to_be_hidden()
    expect(result_locator).to_contain_text(f'Project created: {project_name}')

def test_cancel_project(dialogs_page: Page):
    page = dialogs_page
    project_button_locator = page.locator('#open-modal')
    result_locator = page.get_by_test_id('result')
    project_dialog_locator = page.get_by_role('dialog', name='Create project')
    project_cancel_locator = project_dialog_locator.get_by_role('button', name='Cancel')

    expect(project_button_locator).to_be_visible()
    project_button_locator.click()

    expect(project_dialog_locator).to_be_visible()
    project_cancel_locator.click()

    expect(project_dialog_locator).to_be_hidden()
    expect(result_locator).to_be_empty()
    expect(result_locator).to_be_hidden()

def test_escape_project(dialogs_page: Page):
    page = dialogs_page
    project_button_locator = page.locator('#open-modal')
    result_locator = page.get_by_test_id('result')
    project_dialog_locator = page.get_by_role('dialog', name='Create project')

    expect(project_button_locator).to_be_visible()
    project_button_locator.click()

    expect(project_dialog_locator).to_be_visible()
    page.press('body', key='Escape')

    expect(project_dialog_locator).to_be_hidden()
    expect(result_locator).to_be_hidden()

def test_help_page(dialogs_page: Page):
    page = dialogs_page
    alert_button_locator = page.locator('#alert')
    result_locator = page.get_by_test_id('result')
    help_page_link_locator = page.get_by_role('link', name='Open help in new tab ↗')

    with page.expect_popup() as popup_info:
        help_page_link_locator.click()

    help_page = popup_info.value

    expect(help_page).to_have_url('http://127.0.0.1:8000/help.html')
    expect(help_page).to_have_title('Help · Playwright Lab')

    help_message_locator = help_page.get_by_test_id('help-message')

    expect(help_message_locator).to_have_text('You have successfully opened the help page.')

    help_page.close()

    page.once('dialog', lambda dialog:handle_dialog(dialog, True))
    alert_button_locator.click()

    expect(result_locator).to_contain_text('Alert acknowledged')
