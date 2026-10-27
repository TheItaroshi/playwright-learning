"""Worked N1–N4 examples; run this file explicitly with pytest.

Response expectations observe HTTP; routes control it. Assert the rendered UI
as well, because a correct response does not guarantee correct rendering.
"""

import re
from collections.abc import Iterator
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import APIRequestContext, Page, Playwright, Response, Route, expect


@pytest.fixture
def origin(base_url: str | None) -> str:
    return (base_url or "http://127.0.0.1:8000").rstrip("/")


@pytest.fixture
def network_page(page: Page, origin: str) -> Page:
    page.goto(f"{origin}/index.html#network")
    return page


@pytest.fixture
def api_request(playwright: Playwright, origin: str) -> Iterator[APIRequestContext]:
    # pytest's built-in `request` fixture is not an HTTP client.
    # This standalone context needs no browser, and cleanup runs on failure too.
    api = playwright.request.new_context(base_url=origin)
    try:
        yield api
    finally:
        api.dispose()


def load_products(page: Page, *, status: int, query: str = "", fail: bool = False) -> Response:
    """Click and capture the expected endpoint, method, and query parameters."""
    def matches(response: Response) -> bool:
        url = urlsplit(response.url)
        return (
            url.path == "/api/products"
            and response.request.method == "GET"
            and parse_qs(url.query, keep_blank_values=True)
            == {"q": [query], "fail": ["1" if fail else "0"]}
        )

    # Register before clicking. Check status afterward so an unexpected status
    # fails directly instead of causing a timeout waiting for a different one.
    with page.expect_response(matches) as response_info:
        page.get_by_role("button", name="Load products", exact=True).click()
    response = response_info.value
    assert response.status == status, f"{response.url}: expected {status}, got {response.status}"
    return response


def test_real_products_and_hub_search(network_page: Page) -> None:
    page = network_page
    products = page.locator("#products").get_by_role("article")
    response = load_products(page, status=200)
    assert len(response.json()["products"]) == 4
    expect(products).to_have_count(4)
    expect(page.get_by_test_id("result")).to_have_text("4 products loaded")

    page.get_by_label("Product search", exact=True).fill("hub")
    response = load_products(page, status=200, query="hub")
    assert [product["id"] for product in response.json()["products"]] == ["P103"]
    expect(products).to_have_count(1)
    expect(products.get_by_role("heading")).to_have_text("USB-C hub")


def test_http_error_and_recovery(network_page: Page) -> None:
    page = network_page
    force_error = page.get_by_label("Force HTTP 503")
    result = page.get_by_test_id("result")
    products = page.locator("#products").get_by_role("article")

    force_error.check()
    response = load_products(page, status=503, fail=True)
    assert response.json() == {"error": "Warehouse temporarily unavailable"}
    expect(result).to_have_text("HTTP 503: Warehouse temporarily unavailable")
    expect(result).to_have_class(re.compile(r"\berror\b"))
    expect(products).to_have_count(0)

    force_error.uncheck()
    load_products(page, status=200)
    expect(products).to_have_count(4)
    expect(result).to_have_text("4 products loaded")
    expect(result).not_to_have_class(re.compile(r"\berror\b"))


def test_mock_empty_products(network_page: Page) -> None:
    page = network_page

    def empty_products(route: Route) -> None:
        route.fulfill(status=200, json={"products": []})

    # Include the query string in the pattern. Each test gets a fresh page and
    # context, so this route cannot leak into another test.
    page.route("**/api/products?*", empty_products)
    load_products(page, status=200)
    expect(page.get_by_test_id("result")).to_have_text("No products found")
    expect(page.locator("#products").get_by_role("article")).to_have_count(0)


def test_mock_synthetic_product(network_page: Page) -> None:
    page = network_page

    def synthetic_product(route: Route) -> None:
        route.fulfill(status=200, json={"products": [
            {"id": "MOCK-1", "name": "Practice monitor", "price": 42.5, "stock": 3}
        ]})

    page.route("**/api/products?*", synthetic_product)
    load_products(page, status=200)
    products = page.locator("#products").get_by_role("article")
    expect(products).to_have_count(1)
    expect(products.get_by_role("heading")).to_have_text("Practice monitor")
    expect(products).to_contain_text("$42.50")
    expect(page.get_by_test_id("result")).to_have_text("1 products loaded")


def test_aborted_request_and_retry(network_page: Page) -> None:
    page = network_page
    button = page.get_by_role("button", name="Load products", exact=True)
    result = page.get_by_test_id("result")

    def abort_products(route: Route) -> None:
        route.abort()

    page.route("**/api/products?*", abort_products)
    # An aborted request has no HTTP response: assert the resulting UI instead.
    button.click()
    expect(result).to_have_class(re.compile(r"\berror\b"))
    expect(result).not_to_be_empty()
    expect(page.locator("#products").get_by_role("article")).to_have_count(0)
    expect(button).to_be_enabled()

    # Remove this handler before retrying against the real server.
    page.unroute("**/api/products?*", abort_products)
    load_products(page, status=200)
    expect(page.locator("#products").get_by_role("article")).to_have_count(4)
    expect(result).to_have_text("4 products loaded")
    expect(result).not_to_have_class(re.compile(r"\berror\b"))


def test_api_hub_search(api_request: APIRequestContext) -> None:
    response = api_request.get("/api/products", params={"q": "hub"})
    assert response.status == 200
    products = response.json()["products"]
    assert len(products) == 1
    assert products[0]["id"] == "P103"
    assert products[0]["name"] == "USB-C hub"


def test_api_service_unavailable(api_request: APIRequestContext) -> None:
    response = api_request.get("/api/products", params={"fail": "1"})
    assert response.status == 503
    assert response.json() == {"error": "Warehouse temporarily unavailable"}
