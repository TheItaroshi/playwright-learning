import pytest

from playwright.sync_api import Page, expect

def test_featured_cart(page: Page):
    page.goto('http://127.0.0.1:8000/index.html#locators')
    featured_locator = page.get_by_role('region', name='Featured')
    archive_locator = page.get_by_role('region', name='Archive')

    featured_locator.get_by_role('button').click()
    featured_locator.get_by_role('button').click()

    expect(featured_locator).to_contain_text('Quantity: 2')
    expect(archive_locator).to_contain_text('Quantity: 0')

