import pytest

from playwright.sync_api import Page, expect, Locator

@pytest.fixture
def network_page(page: Page, base_url: str | None) -> Page:
    origin = (base_url or "http://127.0.0.1:8000").rstrip("/")
    page.goto(f"{origin}/index.html#network")
    return page

def expect_response(page: Page, response_trigger: Locator, status: int):
    with (page.expect_response(lambda response: '/api/products?' in response.url
                                                and response.request.method == "GET" ) as response_info):
        response_trigger.click()
    response = response_info.value
    assert response.status == status


def handler_empty_list(route):
    route.fulfill(json={"products": []})

def handler_synthetic_products(route):
    route.fulfill(json={"products": [
        {
            "id": "T1",
            "name": "Test product 1",
            "price": 10,
            "stock": 10
        },
        {
            "id": "T2",
            "name": "Test product 2",
            "price": 99.9,
            "stock": 12
        }
    ]})
def handler_abort(route):
    route.abort()

def test_response_200(network_page: Page):
    page = network_page

    product_search_locator = page.locator('#query')
    load_product_button_locator = page.get_by_role('button', name='Load products')
    products_list_locator = page.locator('#products')
    products_locator = products_list_locator.locator('article')

    expect(products_locator).to_have_count(0)

    expect_response(page, load_product_button_locator, status=200)

    expect(products_locator).to_have_count(4)

    product_search_locator.fill('hub')
    expect_response(page, load_product_button_locator, status=200)

    expect(products_locator).to_have_count(1)
    expect(products_list_locator).to_contain_text('USB-C hub')

def test_response_503(network_page: Page):
    page = network_page

    force_503_locator = page.get_by_label('Force HTTP 503')
    load_product_button_locator = page.get_by_role('button', name='Load products')
    products_list_locator = page.locator('#products')
    products_locator = products_list_locator.locator('article')
    result_locator = page.get_by_test_id('result')

    force_503_locator.check()
    expect_response(page, load_product_button_locator, status=503)

    expect(result_locator).to_have_text('HTTP 503: Warehouse temporarily unavailable')

    force_503_locator.uncheck()
    expect_response(page, load_product_button_locator, status=200)

    expect(products_locator).to_have_count(4)
    expect(result_locator).to_have_text('4 products loaded')

def test_empty_list_mock(network_page: Page):
    page = network_page
    page.route("**/api/products?*", handler_empty_list)
    load_product_button_locator = page.get_by_role('button', name='Load products')
    products_list_locator = page.locator('#products')
    products_locator = products_list_locator.locator('article')
    result_locator = page.get_by_test_id('result')

    expect_response(page, load_product_button_locator, status=200)
    expect(products_locator).to_have_count(0)
    expect(result_locator).to_have_text('No products found')

def test_synthetic_list_mock(network_page: Page):
    page = network_page
    page.route("**/api/products?*", handler_synthetic_products)
    load_product_button_locator = page.get_by_role('button', name='Load products')
    products_list_locator = page.locator('#products')
    products_locator = products_list_locator.locator('article')
    result_locator = page.get_by_test_id('result')

    expect_response(page, load_product_button_locator, status=200)
    expect(products_locator).to_have_count(2)
    expect(products_list_locator).to_contain_text('Test product 1')
    expect(products_list_locator).to_contain_text('Test product 2')
    expect(result_locator).to_have_text('2 products loaded')

def test_abort_mock(network_page: Page):
    page = network_page
    page.route("**/api/products?*", handler_abort)
    load_product_button_locator = page.get_by_role('button', name='Load products')
    result_locator = page.get_by_test_id('result')

    load_product_button_locator.click()

    expect(result_locator).to_have_text('Failed to fetch')