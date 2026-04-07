"""
Citation Generator — generates APA/MLA/Chicago citations from URL or book info.
Uses CrossRef free API for DOI-based citations.
"""
import requests
import re
from datetime import datetime

def fetch_doi_metadata(url_or_doi):
    """Try to fetch metadata for a URL or DOI using CrossRef API."""
    # Extract DOI if present
    doi_match = re.search(r'(10\.\d{4,}/[^\s]+)', url_or_doi)
    if doi_match:
        doi = doi_match.group(1)
    else:
        doi = None

    try:
        if doi:
            resp = requests.get(
                f"https://api.crossref.org/works/{doi}",
                headers={"Accept": "application/json"},
                timeout=10
            )
            if resp.ok:
                data = resp.json().get('message', {})
                return parse_crossref(data)
    except Exception:
        pass

    return None

def parse_crossref(data):
    """Parse CrossRef API response into citation metadata."""
    title = None
    if 'title' in data:
        titles = data['title']
        title = titles[0] if isinstance(titles, list) else titles

    author_list = []
    authors = data.get('author', [])
    for author in authors:
        given = author.get('given', '')
        family = author.get('family', '')
        if given and family:
            author_list.append(f"{family}, {given[0]}.")
        elif family:
            author_list.append(family)

    if len(author_list) > 5:
        authors_str = ', '.join(author_list[:5]) + ', ... '
    else:
        authors_str = ', '.join(author_list) if author_list else 'Unknown Author'

    pub_date = None
    date_parts = data.get('published-print', data.get('published-online', data.get('created', {})))
    date_info = date_parts.get('date-parts', [[]])
    if date_info and date_info[0]:
        date_parts_list = date_info[0]
        year = date_parts_list[0] if len(date_parts_list) > 0 else None
        month = date_parts_list[1] if len(date_parts_list) > 1 else None
        day = date_parts_list[2] if len(date_parts_list) > 2 else None
        if year:
            if month and day:
                pub_date = f"{year}-{month:02d}-{day:02d}"
            else:
                pub_date = str(year)

    publisher = data.get('publisher', 'Unknown Publisher')
    url = data.get('URL', '')

    journal = None
    container = data.get('container-title', [])
    if container:
        journal = container[0] if isinstance(container, list) else container

    volume = data.get('volume', '')
    issue = data.get('issue', '')
    page = data.get('page', '')

    return {
        'title': title or 'Unknown Title',
        'authors': authors_str,
        'year': pub_date[:4] if pub_date else 'n.d.',
        'publisher': publisher,
        'url': url,
        'journal': journal,
        'volume': volume,
        'issue': issue,
        'pages': page,
        'access_date': datetime.now().strftime('%d %B %Y'),
    }

def generate_apa(meta):
    """Generate APA 7th edition citation."""
    authors = meta.get('authors', 'Unknown Author')
    year = meta.get('year', 'n.d.')
    title = meta.get('title', 'Unknown Title')
    url = meta.get('url', '')
    publisher = meta.get('publisher', '')
    journal = meta.get('journal', '')
    volume = meta.get('volume', '')
    issue = meta.get('issue', '')
    pages = meta.get('pages', '')

    if journal:
        # Journal article
        parts = [f"{authors} ({year}). {title}. {journal}"]
        if volume:
            vol_part = f"{volume}"
            if issue:
                vol_part += f"({issue})"
            parts.append(vol_part)
        if pages:
            parts.append(f"{pages}.")
        if url:
            parts.append(f"https://{url}" if not url.startswith('http') else url)
        return ''.join([p + '. ' for p in parts]).strip()
    else:
        # Webpage/website
        parts = [f"{authors} ({year}). {title}. {publisher}."]
        if url:
            parts.append(url)
        return ''.join(parts).strip()

def generate_mla(meta):
    """Generate MLA 9th edition citation."""
    authors = meta.get('authors', 'Unknown Author')
    title = meta.get('title', 'Unknown Title')
    container = meta.get('journal', meta.get('publisher', 'Website'))
    year = meta.get('year', 'n.d.')
    url = meta.get('url', '')
    access_date = meta.get('access_date', '')

    if meta.get('journal'):
        # Journal article
        parts = [
            f"{authors}.",
            f'"{title}."',
            f"{container},"",
            f"{year},"",
            f"accessed {access_date}." if access_date else "",
            url if url else ""
        ]
    else:
        # Webpage
        parts = [
            f"{authors}.",
            f'"{title}."',
            f"{container},"",
            f"{year},",
            url if url else ""
        ]
    return ' '.join(p for p in parts if p).strip().rstrip(',')

def generate_chicago(meta):
    """Generate Chicago author-date citation."""
    authors = meta.get('authors', 'Unknown Author')
    year = meta.get('year', 'n.d.')
    title = meta.get('title', 'Unknown Title')
    url = meta.get('url', '')
    publisher = meta.get('publisher', '')
    journal = meta.get('journal', '')
    volume = meta.get('volume', '')
    issue = meta.get('issue', '')
    pages = meta.get('pages', '')

    if journal:
        parts = [
            f"{authors}.",
            f"{year}.",
            f'"{title}."',
            f"{journal}",
        ]
        if volume:
            vol_part = f"{volume}"
            if issue:
                vol_part += f", no. {issue}"
            parts.append(vol_part)
        if pages:
            parts.append(f": {pages}")
        parts.append(".")
        if url:
            parts.append(f" {url}.")
        return ''.join(parts).strip()
    else:
        parts = [
            f"{authors}.",
            f"{year}.",
            f'"{title}."',
            f"{publisher}.",
            url if url else ""
        ]
        return ' '.join(p for p in parts if p).strip()

def generate_citations(url_or_text, formats=None):
    """Main citation generator. Returns dict of citations."""
    if formats is None:
        formats = ['apa', 'mla', 'chicago']

    meta = fetch_doi_metadata(url_or_text)
    if not meta:
        # Try to parse as manual entry
        return {
            'error': 'Could not fetch citation data. Try entering more details manually.',
            'apa': f'Author. ({datetime.now().year}). Title. URL',
            'mla': f'Author. "Title." Website, accessed {datetime.now().strftime("%d %B %Y")}. URL.',
            'chicago': f'Author. {datetime.now().year}. "Title." Website. URL'
        }

    citations = {}
    for fmt in formats:
        if fmt == 'apa':
            citations['apa'] = generate_apa(meta)
        elif fmt == 'mla':
            citations['mla'] = generate_mla(meta)
        elif fmt == 'chicago':
            citations['chicago'] = generate_chicago(meta)

    citations['meta'] = meta
    return citations
