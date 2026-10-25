from playwright.sync_api import Page, expect

def test_featured_cart(page: Page):
    page.goto('http://127.0.0.1:8000/index.html#locators')
    featured_locator = page.get_by_role('region', name='Featured')
    archive_locator = page.get_by_role('region', name='Archive')
    add_to_cart_button = featured_locator.get_by_role('button', name='Add to cart')

    add_to_cart_button.click()
    add_to_cart_button.click()

    expect(featured_locator).to_contain_text('Quantity: 2')
    expect(archive_locator).to_contain_text('Quantity: 0')

def test_disclosure(page: Page):
    page.goto('http://127.0.0.1:8000/index.html#locators')
    details_locator = page.locator('details').filter(has_text='Delivery details')
    details_summary_locator = details_locator.locator('summary')
    delivery_message = details_locator.get_by_text('Free delivery on orders over $100.')

    expect(delivery_message).to_be_hidden()
    expect(details_locator).not_to_have_attribute('open')

    details_summary_locator.click()

    expect(delivery_message).to_be_visible()
    expect(details_locator).to_have_attribute('open')

    details_summary_locator.click()

    expect(delivery_message).to_be_hidden()
    expect(details_locator).not_to_have_attribute('open')
