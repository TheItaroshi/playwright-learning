import pytest

from playwright.sync_api import Page, expect

@pytest.fixture
def board_page(page: Page, base_url: str | None) -> Page:
    origin = (base_url or "http://127.0.0.1:8000").rstrip("/")
    page.goto(f"{origin}/index.html#board")
    return page


def test_drag(board_page: Page):
    page = board_page
    board_locator = page.locator('.board')
    todo_section_locator = board_locator.get_by_label('To do')
    progress_section_locator = board_locator.get_by_label('In progress')
    first_test_locator = todo_section_locator.get_by_text('Write first test')

    tasks_in_todo = todo_section_locator.get_by_role('article')
    tasks_in_progress = progress_section_locator.get_by_role('article')

    expect(tasks_in_todo).to_have_count(2)
    expect(tasks_in_progress).to_have_count(1)

    first_test_locator.drag_to(progress_section_locator)

    expect(tasks_in_todo).to_have_count(1)
    expect(tasks_in_progress).to_have_count(2)

