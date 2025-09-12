import logging
import urllib.parse

def get_duckduckgo_favicon(url: str):
    """
    Get favicon using DuckDuckGo's favicon service.

    Args:
        url (str): The website URL

    Returns:
        str: DuckDuckGo favicon URL
    """
    try:
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc

        if domain.startswith('www.'):
            domain = domain[4:]

        return f"https://icons.duckduckgo.com/ip3/{domain}.ico"

    except Exception as e:
        logging.error(f"Error getting DuckDuckGo favicon: {e}")
        return None

def extract_site_name(url: str):
    """
    Extract a pretty site name from a URL without scraping.

    Args:
        url (str): The URL to extract the site name from

    Returns:
        str: Pretty site name based on domain
    """
    try:
        # Parse the URL to get the domain
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower()

        if domain.startswith('www.'):
            domain = domain[4:]

        domain = domain.split(':')[0]

        domain_parts = domain.split('.')

        common_tlds = {'com', 'org', 'net', 'edu', 'gov', 'io', 'co', 'uk', 'de', 'fr', 'jp', 'au', 'ca'}

        if len(domain_parts) >= 3 and domain_parts[-1] in common_tlds:
            if len(domain_parts) >= 3 and f"{domain_parts[-2]}.{domain_parts[-1]}" in {'co.uk', 'com.au', 'co.jp', 'co.kr'}:
                main_domain = domain_parts[-3]
            else:
                main_domain = domain_parts[-2]
        else:
            main_domain = domain_parts[0]

        clean_name = main_domain.replace('-', ' ').replace('_', ' ')

        pretty_name = ' '.join(word.capitalize() for word in clean_name.split())

        return pretty_name

    except Exception as e:
        logging.error(f"Error extracting site name: {e}")
        return "Unknown Site"