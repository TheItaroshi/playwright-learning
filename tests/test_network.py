import pytest

from playwright.sync_api import Page, expect, Locator

@pytest.fixture
def network_page(page: Page, base_url: str | None) -> Page:
    origin = (base_url or "http://127.0.0.1:8000").rstrip("/")
    page.goto(f"{origin}/index.html#network")
    return page

def expect_200(page: Page, response_trigger: Locator):
    with (page.expect_response(lambda response: '/api/products?' in response.url
                                                and response.request.method == "GET" ) as response_info):
        response_trigger.click()
    response = response_info.value
    assert response.status == 200
    return response.ok

def expect_503(page: Page, response_trigger: Locator):
    with (page.expect_response(lambda response: '/api/products?' in response.url
                                                and response.request.method == "GET" ) as response_info):
        response_trigger.click()
    response = response_info.value
    assert response.status == 503
    return response.ok

def test_response_200(network_page: Page):
    page = network_page

    product_search_locator = page.locator('#query')
    load_product_button_locator = page.get_by_role('button', name='Load products')
    products_list_locator = page.locator('#products')
    products_locator = products_list_locator.locator('article')

    expect(products_locator).to_have_count(0)

    expect_200(page, load_product_button_locator)

    expect(products_locator).to_have_count(4)

    product_search_locator.fill('hub')
    expect_200(page, load_product_button_locator)

    expect(products_locator).to_have_count(1)

def test_response_503(network_page: Page):
    page = network_page

    force_503_locator = page.get_by_label('Force HTTP 503')
    load_product_button_locator = page.get_by_role('button', name='Load products')
    result_locator = page.get_by_test_id('result')

    force_503_locator.check()
    expect_503(page, load_product_button_locator)

    expect(result_locator).to_have_text('HTTP 503: Warehouse temporarily unavailable')

    force_503_locator.uncheck()
    expect_200(page, load_product_button_locator)

    expect(result_locator).to_have_text('4 products loaded')
