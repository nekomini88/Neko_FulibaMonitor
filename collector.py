import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict
from config import SECTIONS

HEADERS = {"User-Agent": "Mozilla/5.0 (FulibaMonitorBot/1.0; +https://github.com/yourusername/fuliba-monitor)"}

def fetch_section(url: str) -> List[Dict]:
    """
    Fetch a given section URL and extract article links and titles.
    Returns a list of dictionaries with keys: title, link, pub_date (optional).
    Filters out forum links like member.php?mod=logging&action=login.
    """
    try:
        resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=10.0)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    items = []

    # Find all anchor tags with href and non-empty text
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href:
            continue
        # Make absolute URL
        link = urljoin(url, href)
        # Only keep links on the same domain
        if urlparse(link).netloc != urlparse(url).netloc:
            continue
        # Filter out forum links
        if 'member.php' in link or 'mod=logging' in link:
            continue
        title = a.get_text(strip=True)
        if not title or len(title) < 5:  # skip very short text (likely icons/spaces)
            continue
        # Try to find a publication date nearby (look for time tag or date-like text in parent)
        pub_date = None
        # Look for a <time> tag within the same parent or nearby
        time_tag = a.find_next('time')
        if time_tag and time_tag.get('datetime'):
            pub_date = time_tag['datetime']
        elif time_tag and time_tag.get_text(strip=True):
            # We'll store the raw string; scorer can try to parse if needed
            pub_date = time_tag.get_text(strip=True)
        items.append({
            "title": title,
            "link": link,
            "pub_date": pub_date
        })

    # The items are in the order they appear on the page; we assume the first is the latest.
    return items

def gather_sources() -> List[Dict]:
    """
    Gather articles from all sections defined in config.SECTIONS.
    Returns a list of article dicts ordered by section order and then by appearance on page.
    """
    all_items = []
    for section_url in SECTIONS:
        items = fetch_section(section_url)
        if items:
            # We extend with items from this section
            all_items.extend(items)
    return all_items