import pytest

from playwright.sync_api import Page, expect

@pytest.fixture
def network_page(page: Page, base_url: str | None) -> Page:
    origin = (base_url or "http://127.0.0.1:8000").rstrip("/")
    page.goto(f"{origin}/index.html#network")
    return page


def test_response_200(network_page: Page):
    page = network_page

    product_search_locator = page.locator('#query')
    load_product_button_locator = page.get_by_role('button', name='Load products')
    products_list_locator = page.locator('#products')
    products_locator = products_list_locator.locator('article')

    expect(products_locator).to_have_count(0)

    load_product_button_locator.click()

    expect(products_locator).to_have_count(4)

    product_search_locator.fill('hub')
    load_product_button_locator.click()

    expect(products_locator).to_have_count(1)
