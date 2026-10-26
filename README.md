# Playwright Lab

A local website to practice browser automation, from basic form controls to a complete checkout. **You write the tests.** This learning repository also contains personal practice tests and separate worked references for comparison.

## Run

From this project directory:

```sh
python3 playground/server.py
```

Open **http://127.0.0.1:8000**. Keep the terminal running; stop with `Ctrl+C`.

Requires Python 3.10 or newer. No packages, database, build step, accounts, external assets, or internet connection are needed. The server listens only on your computer's loopback interface.

If port 8000 is occupied:

```sh
python3 playground/server.py --port 8001
```

Use the Python server rather than opening the HTML file directly: the network and checkout exercises need its API, and the frame exercise expects a same-origin HTTP page. Run configuration in PyCharm: script `playground/server.py`, using your existing Python interpreter.

## Python learning path

Open **http://127.0.0.1:8000/guide.html** for Python/pytest setup, a recommended exercise order, and wider assignments covering fixtures, traces, cross-browser execution, API testing, isolation, clock control, parallel runs, and CI. Each exercise includes a **Python features to use** panel and detailed assignments with completion criteria below the playground. See [tests/README.md](tests/README.md) for existing practice tests and worked references.

Start with C1 (save a complete profile), then C2 (validation). Use the synchronous Python API consistently. The website needs no dependencies; your test environment needs pytest-playwright and its browser binaries as explained in the guide.

## Exercises

Each exercise has a direct URL and a mission panel with goals, expected results, and practice concepts.

| Route | Practice |
| --- | --- |
| `/#controls` | Text, email, native select, multiple select, radio, checkbox, date, validation |
| `/#locators` | Repeated labels, scoped collections, test IDs, expandable content |
| `/#timing` | Loading states, delayed rendering, disabled controls, auto-waiting |
| `/#tables` | Search, filters, sorting, pagination, row actions, confirmation |
| `/#dialogs` | Alert, confirm, prompt, modal, new tab |
| `/#files` | Single/multiple uploads, preview, deterministic CSV download |
| `/#boundaries` | Same-origin iframe, parent messaging, open shadow DOM |
| `/#board` | Drag-and-drop, accessible move controls, contenteditable, keyboard shortcut |
| `/#network` | Real fetch requests, response mocking, deliberate 503, empty results |
| `/#checkout` | Cart, inventory, discount, delivery, validation, order API, retries |
| `/#storage` | Demo login, sessionStorage, localStorage, browser context isolation |

Start with controls and locators, then choose exercises by interest. For each, cover the happy path, an invalid input or cancellation, and reset/repetition. The app is independent of whether you choose Python or JavaScript/TypeScript for your automation.

## Repeatability contract

- **Reset exercise** restores the current exercise. Navigating away and back also recreates it, except for the explicitly persisted storage exercise.
- The storage exercise's Reset button removes only `lab-session` and `lab-theme`. Sign-in persists in `sessionStorage`; the accent preference persists in `localStorage`. Session storage is not captured by Playwright's `storageState`.
- Data is fixed; there are no random IDs, external requests, current-date dependencies, or random failures.
- Report rendering waits 1,200 ms, then approval enables after another 800 ms. Product API replies wait 800 ms. Valid orders wait 1,000 ms. These are nominal delays; event-loop scheduling can add time. Assert observable state instead of sleeping for these durations.
- Exercise navigation/reset cancels pending timers and aborts active fetches.
- Orders are stateless and always return `ORD-1001`. They do not reduce stock or persist purchases. Separate browser contexts can run in parallel without a shared database reset.
- Browser-local state belongs to your browser context. Reuse contexts deliberately for the storage exercise; use fresh contexts for isolation.
- Native labels and semantic roles are available throughout. Selected outputs also expose `data-testid` values. You choose how to locate elements.
- Text file previews read up to 4 KB per file. Uploads never leave the browser.
- This is a training app: login is simulated, orders are fictional, and no real payments are made.

## API reference

Use these endpoints for response observation, interception, and API assertions:

- `GET /api/health` → `200`, `{"status":"ok"}`.
- `GET /api/products` → `200`, object containing a `products` array with four entries.
- `GET /api/products?q=hub` → one product, `P103`.
- `GET /api/products?fail=1` → `503`, `{"error":"Warehouse temporarily unavailable"}`.
- `POST /api/orders` → `201` on success; `422` for invalid orders or coupons, `400` for an invalid body size.

Order request shape:

```json
{
  "items": {"P101": 1, "P103": 1},
  "email": "learner@example.com",
  "coupon": "LEARN10",
  "shipping": "express"
}
```

Expected response: `{"id":"ORD-1001","total":132.6,"status":"confirmed"}`.

Inventory: P101 keyboard $89 / stock 8; P102 headphones $129 / stock 5; P103 hub $45 / stock 12; P104 lamp $35 / stock 0. Quantities must be positive integers within stock. `LEARN10` discounts products by 10%; standard delivery is free, express adds $12 after the discount. Leave the coupon empty for no discount. Zero-quantity products must be omitted from the request.

## Repository organization

Keep the playground and your automation in this repository. Write tests in `tests/`, starting with `tests/test_controls.py`; add shared fixtures in `tests/conftest.py` when needed. This keeps the practice website, upload fixtures, and tests versioned together and makes a future CI setup simpler. A separate repository is useful later if you want to distribute the playground independently.

Commit source files, documentation, and your tests. The `.gitignore` excludes the virtual environment, IDE settings, test outputs, local secrets, and common browser-state files.

## Files

- `playground/server.py` — standard-library HTTP server and API.
- `playground/dist/` — editable HTML, CSS, JavaScript, frame, popup, and report fixture. No compilation needed; edit and refresh.
- `playground/fixtures/` — files for upload exercises.
- [tests/test_controls.py](tests/test_controls.py) — profile submission and form validation practice.
- [tests/test_locators.py](tests/test_locators.py) — scoped locators and disclosure behavior.
- [tests/test_timing.py](tests/test_timing.py) — auto-waiting and controlled browser-clock practice.
- [tests/test_tables.py](tests/test_tables.py) — filtering, sorting, pagination, account changes, and cancellation.
- [tests/controls_pro_reference.py](tests/controls_pro_reference.py) and [tests/tables_pro_reference.py](tests/tables_pro_reference.py) — worked examples, excluded from automatic pytest collection; explicit run commands are in [tests/README.md](tests/README.md).
- [LEARNING_CONTEXT.md](LEARNING_CONTEXT.md) — learning preferences and handoff context.

Put your automation wherever you prefer in this workspace. The learning material now targets Python with pytest and the synchronous Playwright API; you implement and organize the test suite.

## Implementation validation

Python compilation and JavaScript syntax checks pass. Server request handling was checked in-process for successful orders, invalid inventory and coupons, malformed input, product filtering, and the deliberate 503 response. Live browser verification could not be performed in the build environment because local port binding was denied and no browser was available.
