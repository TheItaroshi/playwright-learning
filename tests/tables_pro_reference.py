"""Worked tables lesson; run explicitly to keep it separate from practice tests."""

import pytest
from playwright.sync_api import Dialog, Locator, Page, expect


ACTIVE_NAMES = [
    "Amelia Brown", "James Taylor", "Liam Chen", "Lucas Anderson",
    "Mia Thomas", "Noah Davis", "Olivia Martin", "Sophia Miller",
]


@pytest.fixture
def tables_page(page: Page, base_url: str | None) -> Page:
    origin = (base_url or "http://127.0.0.1:8000").rstrip("/")
    page.goto(f"{origin}/index.html#tables")
    return page


def collect_statuses(page: Page, *, page_count: int) -> dict[str, str]:
    """Read this exercise's four-row pages, starting on page one.

    A fixed, expected page count bounds traversal and detects missing pages.
    Dictionary insertion order also preserves the displayed name order.
    """
    statuses: dict[str, str] = {}
    previous = page.get_by_role("button", name="Previous", exact=True)
    next_button = page.get_by_role("button", name="Next", exact=True)
    expect(previous).to_be_disabled()

    for page_number in range(1, page_count + 1):
        expect(page.locator("#pages")).to_have_text(
            f"Page {page_number} of {page_count} · {page_count * 4} people"
        )
        rows = page.locator("tbody").get_by_role("row")
        expect(rows).to_have_count(4)
        for row in rows.all():
            cells = row.get_by_role("cell")
            expect(cells).to_have_count(4)
            name = cells.nth(1).inner_text()
            assert name not in statuses, f"Duplicate record across pages: {name}"
            statuses[name] = cells.nth(2).inner_text()

        if page_number < page_count:
            expect(next_button).to_be_enabled()
            next_button.click()
        else:
            expect(next_button).to_be_disabled()

    return statuses


def find_person(page: Page, name: str) -> Locator:
    page.get_by_role("searchbox", name="Search people").fill(name)
    row = page.locator("tbody").get_by_role("row").filter(
        has=page.get_by_role("cell", name=name, exact=True)
    )
    expect(row).to_have_count(1)
    return row


def handle_confirmation(dialog: Dialog, *, accept: bool) -> None:
    assert dialog.type == "confirm"
    assert dialog.message == "Deactivate Olivia Martin?"
    if accept:
        dialog.accept()
    else:
        dialog.dismiss()


def test_filters_and_sorts_all_matching_names(tables_page: Page) -> None:
    page = tables_page
    page.get_by_role("searchbox", name="Search people").fill("a")
    page.get_by_label("Status", exact=True).select_option(label="Active")

    ascending = collect_statuses(page, page_count=2)
    assert list(ascending) == ACTIVE_NAMES
    assert set(ascending.values()) == {"Active"}

    # Sorting keeps the current page, so return to page one first.
    page.get_by_role("button", name="Previous", exact=True).click()
    page.get_by_role("button", name="Name ↑", exact=True).click()
    expect(page.locator("#name-header")).to_have_attribute("aria-sort", "descending")
    descending = collect_statuses(page, page_count=2)
    assert list(descending) == ACTIVE_NAMES[::-1]
    assert set(descending.values()) == {"Active"}


def test_deactivation_changes_only_olivia(tables_page: Page) -> None:
    page = tables_page
    before = collect_statuses(page, page_count=3)
    assert before["Olivia Martin"] == "Active"
    row = find_person(page, "Olivia Martin")

    page.once("dialog", lambda dialog: handle_confirmation(dialog, accept=True))
    row.get_by_role("button", name="Deactivate", exact=True).click()

    expect(row.get_by_role("cell").nth(2)).to_have_text("Inactive")
    expect(row.get_by_role("button", name="Activate", exact=True)).to_be_visible()
    expect(page.get_by_test_id("result")).to_have_text("Olivia Martin is now inactive")

    page.get_by_role("searchbox", name="Search people").clear()
    after = collect_statuses(page, page_count=3)
    expected = before.copy()
    expected["Olivia Martin"] = "Inactive"
    assert after == expected


def test_cancelling_deactivation_keeps_olivia_active(tables_page: Page) -> None:
    page = tables_page
    row = find_person(page, "Olivia Martin")
    status = row.get_by_role("cell").nth(2)
    deactivate = row.get_by_role("button", name="Deactivate", exact=True)
    expect(status).to_have_text("Active")

    page.once("dialog", lambda dialog: handle_confirmation(dialog, accept=False))
    deactivate.click()

    expect(status).to_have_text("Active")
    expect(deactivate).to_be_visible()
    expect(page.get_by_test_id("result")).to_be_empty()


def test_unmatched_search_shows_empty_state(tables_page: Page) -> None:
    page = tables_page
    search = page.get_by_role("searchbox", name="Search people")
    search.fill("Nobody Matches This Name")

    rows = page.locator("tbody").get_by_role("row")
    expect(rows).to_have_count(1)
    expect(rows).to_have_text(["No people found"])
    expect(page.locator("#pages")).to_have_text("Page 1 of 1 · 0 people")
    expect(page.get_by_role("button", name="Previous", exact=True)).to_be_disabled()
    expect(page.get_by_role("button", name="Next", exact=True)).to_be_disabled()

    # Clearing the query proves the table can recover from an empty result.
    search.clear()
    expect(rows).to_have_count(4)
    expect(page.locator("#pages")).to_have_text("Page 1 of 3 · 12 people")
