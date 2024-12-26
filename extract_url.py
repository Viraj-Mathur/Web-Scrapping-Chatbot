import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_all_urls(base_url):
    """
    Extracts all unique URLs from the given website.

    Args:
        base_url (str): The URL of the website to scrape.

    Returns:
        list: A list of unique URLs found on the website.
    """
    try:
        # Send a request to the website
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the website content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <a> tags with href attributes
        anchor_tags = soup.find_all('a', href=True)

        # Extract and normalize URLs
        urls = []
        for tag in anchor_tags:
            href = tag['href']
            # Convert relative URLs to absolute URLs
            full_url = urljoin(base_url, href)
            urls.append(full_url)

        # Remove duplicates and return the URLs
        return list(set(urls))

    except requests.RequestException as e:
        print(f"Error fetching {base_url}: {e}")
        return []

if __name__ == "__main__":
    website_url = "https://botpenguin.com/"
    urls = extract_all_urls(website_url)
    print(f"Found {len(urls)} URLs:")
    for url in urls:
        print(url)
