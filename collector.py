import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict
from config import BASE_URL

HEADERS = {"User-Agent": "Mozilla/5.0 (FulibaMonitorBot/1.0; +https://github.com/yourusername/fuliba-monitor)"}

def gather_sources() -> List[Dict]:
    """
    Fetch the homepage of BASE_URL and extract article links and titles.
    Returns a list of dictionaries with keys: title, link, pub_date (optional).
    Filters out forum links like member.php?mod=logging&action=login.
    """
    base_url = BASE_URL
    try:
        resp = httpx.get(base_url, headers=HEADERS, follow_redirects=True, timeout=10.0)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching {base_url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    items = []

    # Find all anchor tags with href and non-empty text
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href:
            continue
        # Make absolute URL
        link = urljoin(base_url, href)
        # Only keep links on the same domain
        if urlparse(link).netloc != urlparse(base_url).netloc:
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
    # We'll return all, but scheduler will take the first.
    return items