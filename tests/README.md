# Your Python tests

Write your own Playwright + pytest tests here, starting with `test_controls.py`.
Use the synchronous API from `playwright.sync_api`. The learning path at
http://127.0.0.1:8000/guide.html explains setup and assignments.

Suggested organization as your suite grows:

- `test_controls.py`, `test_locators.py`, etc.: independent tests per exercise.
- `conftest.py`: shared pytest fixtures once you need them.
- `pages/`: optional page objects once repeated workflows justify them.

Keep reusable upload files in `playground/fixtures/`. Use pytest's `tmp_path`
for generated downloads and saved browser state. Do not commit authentication
state, traces, or local environment files.

The automation is learning work; worked references are available for comparison.

## Basic controls

- `test_controls.py` contains practice tests.
- `controls_pro_reference.py` is the self-describing pro example. Pytest skips it during automatic collection; run it explicitly with `pytest tests/controls_pro_reference.py`.

## Locators

- [test_locators.py](test_locators.py) covers scoping the duplicate Add to cart button to Featured, checking Archive stays unchanged, and opening and closing Delivery details.

## Timing

- [test_timing.py](test_timing.py) covers report loading and approval using auto-waiting, plus a separate paused-clock test for the 1,200 ms report delay and the additional 800 ms approval delay.

Run all practice tests from the project root with `.venv/bin/python -m pytest tests -v --headed` while the playground server is running. To focus on one lesson, replace `tests` with its file path, such as `tests/test_timing.py`.

## Tables

- `test_tables.py` contains practice tests.
- `tables_pro_reference.py` covers sorting across pages, changing only one account, cancellation, and empty-search recovery. It uses a navigation fixture and small helpers; its page collector expects this exercise's full four-row pages.
- Run the reference explicitly with `.venv/bin/python -m pytest tests/tables_pro_reference.py -v --headed` while the playground server is running. It is excluded from automatic collection.
