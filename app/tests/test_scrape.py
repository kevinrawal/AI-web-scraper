import sys
import os
import io
from unittest.mock import patch, MagicMock
from selenium.common.exceptions import TimeoutException, WebDriverException
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# pylint: disable=C0413
from app.scrape import scrape_data, parse_page_data, fetch_page_source

# Mock HTML content
SAMPLE_HTML = """
<html>
<head><title>Test Page</title></head>
<body>
    <h1>Main Header</h1>
    <p>Sample paragraph.</p>
    <a href="https://example.com">Example Link</a>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
    <table>
        <tr><th>Header 1</th><th>Header 2</th></tr>
        <tr><td>Data 1</td><td>Data 2</td></tr>
    </table>
</body>
</html>
"""


@patch("app.scrape.fetch_page_source")
def test_scrape_data(mock_fetch_page_source):
    """
    This function tests the scrape_data function by mocking the fetch_page_source function.
    It checks if the scrape_data function correctly extracts the title and content from the HTML page.
    The content is checked for headers, paragraphs, links, list items, and table content.
    """
    mock_fetch_page_source.return_value = SAMPLE_HTML

    url = "https://example.com"
    data = scrape_data(url)

    assert data["title"] == "Test Page"
    assert len(data["content"]) > 0

    # Check headers
    headers = [item["text"] for item in data["content"] if item["type"] == "header"]
    assert "Main Header" in headers

    # Check paragraphs
    paragraphs = [
        item["text"] for item in data["content"] if item["type"] == "paragraph"
    ]
    assert "Sample paragraph." in paragraphs

    # Check links
    links = [item["href"] for item in data["content"] if item["type"] == "link"]
    assert "https://example.com" in links

    # Check list items
    lists = [item["items"] for item in data["content"] if item["type"] == "list"]
    assert lists[0] == ["Item 1", "Item 2"]

    # Check table content
    tables = [item["rows"] for item in data["content"] if item["type"] == "table"]
    assert tables[0] == [["Header 1", "Header 2"], ["Data 1", "Data 2"]]


def test_parse_page_data():
    """
    Tests the functionality of the parse_page_data function directly without Selenium.
    Verifies that the function correctly extracts the title and content from the HTML page.
    """

    parsed_data = parse_page_data(SAMPLE_HTML)

    assert parsed_data["title"] == "Test Page"
    assert len(parsed_data["content"]) > 0

    headers = [
        item["text"] for item in parsed_data["content"] if item["type"] == "header"
    ]
    assert "Main Header" in headers


@patch("app.scrape.webdriver.Chrome")
@patch("sys.stdout", new_callable=io.StringIO)
def test_fetch_page_source_timeout(mock_stdout, mock_chrome_driver):
    """
    Tests the functionality of the fetch_page_source function with a timeout exception.

    Args:
        mock_stdout (io.StringIO): A mock object for the stdout stream.
        mock_chrome_driver (MagicMock): A mock object for the Chrome WebDriver.
    """
    mock_driver_instance = MagicMock()
    mock_chrome_driver.return_value = mock_driver_instance
    mock_driver_instance.get.side_effect = TimeoutException("Page load timed out")

    url = "http://example.com"

    result = fetch_page_source(url)

    output = mock_stdout.getvalue().strip()
    assert "TimeoutException: Failed to load" in output
    assert "http://example.com" in output

    assert result == ""


@patch("app.scrape.webdriver.Chrome")
@patch("sys.stdout", new_callable=io.StringIO)
def test_fetch_page_source_webdriver_exception(mock_stdout, mock_chrome_driver):
    """
    Tests the functionality of the fetch_page_source function with a WebDriver exception

    Args:
        mock_stdout (io.StringIO): A mock object for the stdout stream.
        mock_chrome_driver (MagicMock): A mock object for the Chrome WebDriver.
    """
    mock_driver_instance = MagicMock()
    mock_chrome_driver.return_value = mock_driver_instance
    mock_driver_instance.get.side_effect = WebDriverException("WebDriver failed")

    url = "http://example.com"

    result = fetch_page_source(url)

    output = mock_stdout.getvalue().strip()
    assert "WebDriverException: An error occurred" in output
    assert "WebDriver failed" in output

    assert result == ""


if __name__ == "__main__":
    pytest.main()
