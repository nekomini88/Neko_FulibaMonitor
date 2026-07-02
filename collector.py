import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Optional

HEADERS = {"User-Agent": "Mozilla/5.0 (FulibaMonitorBot/1.0; +https://github.com/yourusername/fuliba-monitor)"}

def fetch_article_from_section(section_url: str) -> Optional[Dict[str, str]]:
    """
    Fetch a section URL and extract the first article's title and link.
    Returns a dict with keys: title, link, or None if not found.
    """
    try:
        resp = httpx.get(section_url, headers=HEADERS, follow_redirects=True, timeout=10.0)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching {section_url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')
    # Find the first article focus link
    focus_a = soup.select_one('a.focus')
    if not focus_a or not focus_a.has_attr('href'):
        return None

    link = focus_a['href']
    # Make sure it's absolute
    if not link.startswith('http'):
        link = urljoin(section_url, link)

    # Try to get title from img alt
    title = None
    img = focus_a.find('img')
    if img and img.has_attr('alt'):
        title = img['alt'].strip()

    # If not found, try to find a header h2 a with matching href
    if not title:
        # Look for h2 a with href exactly matching link (or containing)
        h2_a = soup.select_one(f'h2 a[href="{link}"]')
        if h2_a:
            title = h2_a.get_text(strip=True)
        else:
            # Fallback: maybe the link text itself (though often empty for image links)
            link_text = focus_a.get_text(strip=True)
            if link_text:
                title = link_text
    if not title:
        title = "未获取到标题"

    return {"title": title, "link": link}

# For backward compatibility, we keep a stub if needed elsewhere
def gather_sources() -> List[Dict[str, str]]:
    """
    This function is kept for compatibility but not used in the current scheduler.
    We'll iterate over sections in scheduler and call fetch_article_from_section directly.
    """
    # This function is not used in the current design, but we keep it to avoid import errors.
    return []