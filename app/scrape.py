import os
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup


def fetch_page_source(url: str) -> str:
    """
    Fetches the HTML page source of a given URL using Selenium WebDriver in headless mode.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        str: The HTML page source of the webpage.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(script_dir, "chromedriver.exe")

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Headless mode
    driver = webdriver.Chrome(
        service=Service(chromedriver_path), options=chrome_options
    )

    try:
        driver.get(url)
        page_source = driver.page_source
    except TimeoutException:
        print(f"TimeoutException: Failed to load {url}")
        page_source = ""
    except WebDriverException as e:
        print(f"WebDriverException: An error occurred: {str(e)}")
        page_source = ""
    finally:
        driver.quit()

    return page_source


def get_content(element) -> List[Dict]:
    """
    Recursively extracts the content from a given BeautifulSoup element and its children.

    Args:
        element (BeautifulSoup element): The element to extract content from.

    Returns:
        List[Dict]: A list of dictionaries representing the extracted content. Each dictionary contains the following keys:
            - 'type' (str): The type of content ('header', 'paragraph', 'link', 'list', 'table', or 'text').
            - 'text' (str): The text content of the element.
            - 'tag' (str): The HTML tag name of the element (only for 'header' type).
            - 'href' (str): The href attribute of the element (only for 'link' type).
            - 'items' (List[str]): The list items (only for 'list' type).
            - 'ordered' (bool): Indicates whether the list is ordered or not (only for 'list' type).
            - 'rows' (List[List[str]]): The rows of the table (only for 'table' type).
    """

    content = []
    for child in element.children:
        if child.name:
            tag_name = child.name.lower()
            if tag_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                content.append(
                    {"type": "header", "text": child.text.strip(), "tag": tag_name}
                )
            elif tag_name == "p":
                content.append({"type": "paragraph", "text": child.text.strip()})
            elif tag_name == "a" and child.get("href"):
                content.append(
                    {"type": "link", "text": child.text.strip(), "href": child["href"]}
                )
            elif tag_name == "ul" or tag_name == "ol":
                # Handle lists
                items = [li.text.strip() for li in child.find_all("li")]
                content.append(
                    {"type": "list", "items": items, "ordered": tag_name == "ol"}
                )
            elif tag_name == "table":
                # Handle tables
                rows = []
                for row in child.find_all("tr"):
                    cells = [cell.text.strip() for cell in row.find_all(["td", "th"])]
                    rows.append(cells)
                content.append({"type": "table", "rows": rows})
            else:
                # Recursively handle other elements
                content.extend(get_content(child))
        elif isinstance(child, str):
            # Handle raw text nodes
            if child.strip():
                content.append({"type": "text", "text": child.strip()})

    return content


def parse_page_data(page_source: str) -> Dict:
    """
    Parse the page source using BeautifulSoup and return a structured dictionary
    that captures the hierarchy of content.

    Args:
        page_source (str): The HTML source of the page to parse.

    Returns:
        Dict: A dictionary containing the title and content of the page.
    """
    soup = BeautifulSoup(page_source, "html.parser")

    # Start from the body element of the page
    body_content = get_content(soup.body)

    page_data = {
        "title": soup.title.string if soup.title else "No title",
        "content": body_content,
    }

    return page_data


def scrape_data(url: str) -> Dict:
    """
    Scrapes data from a given URL by fetching its page source and parsing it.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        Dict: A dictionary containing the title and content of the scraped page.
    """

    page_source = fetch_page_source(url)
    page_data = parse_page_data(page_source)
    return page_data
