import datetime

from playwright.sync_api import Page, expect

def test_featured_cart(page: Page):
    page.goto('http://127.0.0.1:8000/index.html#timing')
    load_button_locator = page.get_by_role('button', name='Load report')
    transaction_count_locator = page.get_by_test_id('transaction-count')
    result_locator = page.get_by_test_id('result')

    expect(transaction_count_locator).to_be_hidden()
    expect(result_locator).to_be_hidden()
    load_button_locator.click()

    transaction_count_locator.wait_for(state='visible')

    expect(transaction_count_locator).to_have_text('42')

    approve_button_locator = page.get_by_role('button', name='Approve report')

    expect(approve_button_locator).to_be_enabled()
    approve_button_locator.click()

    expect(result_locator).to_be_visible()

