import pytest
import csv

from pathlib import Path

from playwright.sync_api import Page, expect

@pytest.fixture
def files_page(page: Page, base_url: str | None) -> Page:
    origin = (base_url or "http://127.0.0.1:8000").rstrip("/")
    page.goto(f"{origin}/index.html#files")
    return page

def get_fixtures_dir():
    fixtures_dir = Path(__file__).resolve().parent.parent / 'playground' / 'fixtures'
    return fixtures_dir


def test_files_upload(files_page: Page):
    page = files_page
    fixtures_dir = get_fixtures_dir()
    files_to_upload = {
        'profile.json': fixtures_dir / 'profile.json',
        'notes.txt': fixtures_dir / 'notes.txt',
    }

    with page.expect_file_chooser() as fc_info:
        page.locator("#upload").click()

    file_chooser = fc_info.value
    file_chooser.set_files(list(files_to_upload.values()))

    file_list_locator = page.locator('#file-list')
    file_preview_locator = file_list_locator.locator('.result')
    expect(file_preview_locator).to_have_count(2)

    for file_name in files_to_upload.keys():
        with open(files_to_upload[file_name]) as f:
            file_content = f.read()

        file_preview = file_preview_locator.filter(has=page.get_by_text(file_name, exact=True))
        expect(file_preview.locator('pre')).to_have_text(file_content)

    file_chooser.set_files([])
    expect(file_preview_locator).to_have_count(0)

def test_download_report(files_page: Page, tmp_path):
    expected_result = [
        'id name status',
        '1 Olivia Martin Active',
        '2 Liam Chen Active',
        '3 Emma Wilson Inactive',
    ]

    page = files_page

    with page.expect_download() as download_info:
        page.get_by_text("Download report").click()

    download = download_info.value
    download_file_name = download.suggested_filename
    download_file_path = tmp_path / download_file_name

    download.save_as(download_file_path)

    with open(download_file_path) as csv_report:
        report_reader = csv.reader(csv_report)
        for row_id, row in enumerate(report_reader):
            assert ' '.join(row) == expected_result[row_id]
