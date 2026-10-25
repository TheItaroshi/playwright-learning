import datetime

from playwright.sync_api import Page, expect

def test_report_approval(page: Page):
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
    expect(result_locator).to_have_text('Report approved')

def test_report_approval_with_clock(page: Page):
    page.clock.install(time=datetime.datetime(2026, 1, 1, 10, 0, 0))
    page.goto('http://127.0.0.1:8000/index.html#timing')
    page.clock.pause_at(datetime.datetime(2026, 1, 1, 10, 1, 0))
    load_button_locator = page.get_by_role('button', name='Load report')
    transaction_count_locator = page.get_by_test_id('transaction-count')
    report_locator = page.locator('#report')
    result_locator = page.get_by_test_id('result')

    expect(transaction_count_locator).to_be_hidden()
    expect(result_locator).to_be_hidden()
    load_button_locator.click()

    page.clock.run_for(1199)
    expect(report_locator).to_contain_text("Preparing report")
    expect(transaction_count_locator).to_be_hidden()

    page.clock.run_for(1)
    expect(report_locator).to_contain_text("Report ready")
    expect(transaction_count_locator).to_be_visible()
    expect(transaction_count_locator).to_have_text('42')

    approve_button_locator = page.get_by_role('button', name='Approve report')

    page.clock.run_for(799)
    expect(approve_button_locator).to_be_disabled()

    page.clock.run_for(1)
    expect(approve_button_locator).to_be_enabled()
    approve_button_locator.click()

    expect(result_locator).to_be_visible()
    expect(result_locator).to_have_text('Report approved')
