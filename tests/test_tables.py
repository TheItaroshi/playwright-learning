from playwright.sync_api import Page, expect

def get_name_values(page, table_values=None):
    if table_values is None:
        table_values = []
    table_locator = page.locator('tbody')
    rows = table_locator.get_by_role('row')

    for row in rows.all():
        cells = row.get_by_role('cell')
        expect(cells).to_have_count(4)
        table_values.append(cells.nth(1).inner_text())

    return table_values

def get_activation_values(page, activation_values=None):
    if activation_values is None:
        activation_values = {}
    table_locator = page.locator('tbody')
    rows = table_locator.get_by_role('row')

    for row in rows.all():
        cells = row.get_by_role('cell')
        expect(cells).to_have_count(4)
        activation_values[cells.nth(1).inner_text()] = cells.nth(2).inner_text()

    return activation_values

def handle_dialog(dialog, accept:bool):
    if accept:
        dialog.accept()
    else:
        dialog.dismiss()

def test_filter_and_sort(page: Page):
    status_options = {
        'All': 'All',
        'Active': 'Active',
        'Inactive': 'Inactive'
    }

    names = ['Amelia Brown', 'James Taylor', 'Liam Chen', 'Lucas Anderson',
             'Mia Thomas', 'Noah Davis', 'Olivia Martin', 'Sophia Miller']

    reversed_names = names[::-1]


    page.goto('http://127.0.0.1:8000/index.html#tables')
    search_locator = page.get_by_placeholder('Search by name')
    status_locator = page.locator('#filter')
    name_sort_locator = page.locator('#sort')
    next_button_locator = page.locator('#next')
    previous_button_locator = page.locator('#previous')

    search_locator.fill('a')
    status_locator.select_option(status_options['Active'])

    table_values = get_name_values(page=page)

    next_button_locator.click()

    table_values = get_name_values(page=page, table_values=table_values)

    assert table_values == names

    previous_button_locator.click()
    name_sort_locator.click()

    table_values = get_name_values(page=page)

    next_button_locator.click()

    table_values = get_name_values(page=page, table_values=table_values)

    assert table_values == reversed_names


def test_account_modify(page: Page):
    name = 'Olivia Martin'

    page.goto('http://127.0.0.1:8000/index.html#tables')
    search_locator = page.get_by_placeholder('Search by name')
    next_button_locator = page.locator('#next')
    previous_button_locator = page.locator('#previous')

    activation_values = get_activation_values(page=page)
    next_button_locator.click()
    activation_values = get_activation_values(page=page,activation_values=activation_values)
    next_button_locator.click()
    activation_values = get_activation_values(page=page,activation_values=activation_values)

    previous_button_locator.click()
    previous_button_locator.click()

    search_locator.fill(name)
    olivia_cell_locator = page.get_by_role('row').filter(has_text=name)
    olivia_active_button_locator = olivia_cell_locator.get_by_role('button')

    expect(olivia_active_button_locator).to_contain_text('Deactivate')
    page.once("dialog", lambda dialog: handle_dialog(dialog, True))
    olivia_active_button_locator.click()
    expect(olivia_active_button_locator).to_contain_text('Activate')

    search_locator.clear()

    new_activation_values = get_activation_values(page=page)
    next_button_locator.click()
    new_activation_values = get_activation_values(page=page,activation_values=new_activation_values)
    next_button_locator.click()
    new_activation_values = get_activation_values(page=page,activation_values=new_activation_values)

    assert activation_values != new_activation_values
    activation_values['Olivia Martin'] = 'Inactive'
    assert activation_values == new_activation_values


def test_account_modification_dismiss(page: Page):

    name = 'Olivia Martin'

    page.goto('http://127.0.0.1:8000/index.html#tables')
    search_locator = page.get_by_placeholder('Search by name')

    search_locator.fill(name)
    olivia_cell_locator = page.get_by_role('row').filter(has_text=name)
    olivia_active_button_locator = olivia_cell_locator.get_by_role('button')

    expect(olivia_active_button_locator).to_contain_text('Deactivate')
    page.once("dialog", lambda dialog: handle_dialog(dialog, False))

    olivia_active_button_locator.click()
    expect(olivia_active_button_locator).to_contain_text('Deactivate')

    table_locator = page.locator('tbody')
    rows = table_locator.get_by_role('row')
    expect(rows).to_contain_text("Active")

    search_locator.clear()

def test_empty_search(page: Page):
    page.goto('http://127.0.0.1:8000/index.html#tables')
    search_locator = page.get_by_placeholder('Search by name')
    table_locator = page.locator('tbody')

    search_locator.fill("Bla bla bla bla bla")
    rows = table_locator.get_by_role('row')
    expect(rows).to_have_count(1)
    expect(rows).to_contain_text("No people found")
