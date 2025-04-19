import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_text_from_url(
    url: str,
    container_selector: str = 'body',
    tag_filter: list[str] = ['p', 'li'],
    base_url: str = None,
    clean_links: bool = True
) -> dict:
    """
    Fetches and parses HTML from the given URL using BeautifulSoup.

    Args:
        url: Full URL to scrape.
        container_selector: CSS selector for the main content block.
        tag_filter: Tags to extract text from (e.g., ['p', 'li']).
        base_url: Base for resolving relative links, optional.
        clean_links: If True, removes <a> tag hrefs but keeps text.

    Returns:
        Dict with 'text', 'title', and optionally 'links'.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (ChatGPT Scraper)'}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, 'html.parser')

    # Extract title
    title = soup.title.string.strip() if soup.title else "No Title"

    # Get container (e.g., main content)
    container = soup.select_one(container_selector)
    if not container:
        container = soup.body

    # Extract text
    extracted = []
    for tag in container.find_all(tag_filter):
        for a in tag.find_all('a'):
            if clean_links:
                a.unwrap()  # Keep text only, remove href
        text = tag.get_text(strip=True)
        if text:
            extracted.append(text)

    return {
        "title": title,
        "text": "\n".join(extracted),
        "url": url
    }
