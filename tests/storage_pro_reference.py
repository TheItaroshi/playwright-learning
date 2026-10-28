"""Worked S1–S4 examples; run explicitly to keep practice tests separate.

The page fixture already has an isolated browser context. Create another
context only when comparing independent sessions or loading saved state.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, expect


EMAIL = "learner@example.com"
PASSWORD = "practice123"


@pytest.fixture
def storage_page(page: Page, base_url: str | None) -> Page:
    origin = (base_url or "http://127.0.0.1:8000").rstrip("/")
    page.goto(f"{origin}/index.html#storage")
    return page


def sign_in(page: Page, *, password: str = PASSWORD) -> None:
    """Submit credentials; each test decides which outcome to expect."""
    page.get_by_label("Email", exact=True).fill(EMAIL)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Sign in", exact=True).click()


def expect_signed_in(page: Page) -> None:
    # The signed-in banner is separate from the result/status output.
    expect(page.get_by_text(f"Signed in as {EMAIL}", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Sign out", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Sign in", exact=True)).to_have_count(0)


def expect_signed_out(page: Page) -> None:
    expect(page.get_by_label("Email", exact=True)).to_be_visible()
    expect(page.get_by_label("Password", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Sign in", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Sign out", exact=True)).to_have_count(0)


def test_session_survives_reload_until_sign_out(storage_page: Page) -> None:
    page = storage_page
    sign_in(page)
    expect_signed_in(page)

    # sessionStorage survives a reload in the same tab.
    page.reload()
    expect_signed_in(page)

    page.get_by_role("button", name="Sign out", exact=True).click()
    expect_signed_out(page)
    # Reload again to prove logout removed the stored session too.
    page.reload()
    expect_signed_out(page)


def test_fresh_context_does_not_share_login_or_theme(
    storage_page: Page, browser: Browser
) -> None:
    page_a = storage_page
    sign_in(page_a)
    expect_signed_in(page_a)
    page_a.get_by_label("Saved accent preference").select_option(label="Ocean")
    expect(page_a.get_by_label("Saved accent preference")).to_have_value("Ocean")

    # A new page in A's context would share localStorage. A fresh context gives
    # B independent storage. Close manually created contexts even on failure.
    context_b = browser.new_context()
    try:
        page_b = context_b.new_page()
        page_b.goto(page_a.url)
        expect_signed_out(page_b)
        expect(page_b.get_by_label("Saved accent preference")).to_have_value("Sage")

        # Check both sides: opening B must not change A's session or theme.
        expect_signed_in(page_a)
        expect(page_a.get_by_label("Saved accent preference")).to_have_value("Ocean")
    finally:
        context_b.close()


def test_saved_state_restores_theme_but_not_session(
    storage_page: Page, browser: Browser, tmp_path: Path
) -> None:
    page_a = storage_page
    sign_in(page_a)
    expect_signed_in(page_a)
    page_a.get_by_label("Saved accent preference").select_option(label="Ocean")
    expect(page_a.get_by_test_id("result")).to_have_text("Preference saved: Ocean")

    # Playwright writes valid JSON directly. tmp_path keeps this test's state
    # file separate from other tests and out of the repository.
    state_path = tmp_path / "storage-state.json"
    page_a.context.storage_state(path=state_path)

    # storage_state includes localStorage (theme), but not sessionStorage
    # (this demo's login). Being signed out in C is the expected outcome.
    context_c = browser.new_context(storage_state=state_path)
    try:
        page_c = context_c.new_page()
        page_c.goto(page_a.url)
        expect_signed_out(page_c)
        expect(page_c.get_by_label("Saved accent preference")).to_have_value("Ocean")

        expect_signed_in(page_a)
        expect(page_a.get_by_label("Saved accent preference")).to_have_value("Ocean")
    finally:
        context_c.close()


def test_wrong_password_keeps_user_signed_out(storage_page: Page) -> None:
    # The page fixture supplies a fresh context for this test automatically.
    page = storage_page
    expect_signed_out(page)
    sign_in(page, password="wrong-password")

    expect(page.get_by_test_id("result")).to_have_text("Incorrect email or password")
    expect_signed_out(page)
    page.reload()
    expect_signed_out(page)
