# scraper_module.py

import requests
from bs4 import BeautifulSoup
import pickle
import re

def sanitize_page_content(page_content):
    """
    Cleans raw webpage text by removing JavaScript, HTML tags,
    and redundant whitespace.
    """
    # Remove JavaScript and CSS
    page_content = re.sub(
        r'<(script|style)\b[^<]*(?:(?!<\/\1>)<[^<]*)*<\/\1>',
        '',
        page_content,
        flags=re.DOTALL
    )
    # Remove HTML tags
    page_content = re.sub(r'<[^>]+>', '', page_content)
    # Remove extra whitespace
    page_content = ' '.join(page_content.split())
    return page_content

def fetch_links(html_content, base_url):
    """
    Extracts all unique links from the HTML content and resolves relative URLs.

    Args:
        html_content (str): The raw HTML content of the webpage.
        base_url (str): The base URL for resolving relative paths.

    Returns:
        dict: A dictionary mapping relative paths to absolute URLs.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    found_links = {}
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        # Skip empty and invalid hrefs
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue
        # Resolve relative URLs to absolute
        if href.startswith('/'):
            found_links[href] = f'{base_url.rstrip("/")}{href}'
        elif href.startswith('http'):
            found_links[href] = href
    return found_links

def scrape_page(url, section_label, selector=None):
    """
    Scrapes a URL, cleans content, and extracts links.

    Args:
        url (str): The URL to scrape.
        section_label (str): A label for the section being scraped.
        selector (str): CSS selector for targeting specific content (optional).

    Returns:
        tuple: Cleaned text content and a dictionary of extracted links.
    """
    print(f"Scraping {section_label} ({url})...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Error accessing {url}: {error}")
        return None, None

    # Parse the HTML response
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract specific content if a selector is provided
    if selector:
        selected_elements = soup.select(selector)
        raw_text = ' '.join([element.get_text() for element in selected_elements])
    else:
        # Default to the entire page text if no selector is given
        raw_text = soup.get_text()

    # Extract links from the HTML
    page_links = fetch_links(soup.prettify(), url)
    print(f"Links Extracted from {section_label}: {len(page_links)}")

    # Clean the raw content
    clean_content = sanitize_page_content(raw_text)

    return clean_content, page_links

def extract_and_store(site_urls, output_filename, selector=None):
    """
    Scrapes multiple URLs and saves structured data to a file.

    Args:
        site_urls (dict): A dictionary of section labels and their URLs.
        output_filename (str): The filename for storing the scraped data.
        selector (str): CSS selector for targeting specific content (optional).
    """
    aggregated_data = {}

    for section, site_url in site_urls.items():
        clean_content, extracted_links = scrape_page(site_url, section, selector)
        if clean_content:
            aggregated_data[section] = {
                'text': clean_content,
                'links': extracted_links
            }
            print(f"Data collected for {section}.")

    # Save the aggregated data to a pickle file
    with open(output_filename, 'wb') as file:
        pickle.dump(aggregated_data, file)
    print(f"Data successfully saved to {output_filename}.")

if __name__ == '__main__':
    # Define the target URLs for scraping
    site_urls = {
        "Homepage": "https://botpenguin.com/",
        "Pricing Details": "https://botpenguin.com/chatbot-pricing",
        "Affiliate Program": "https://botpenguin.com/partners/chatbot-affiliate-program",
        "Ecommerce Sector": "https://botpenguin.com/chatbot-industry/ecommerce",
        "Custom Solutions": "https://botpenguin.com/solutions/custom-chatgpt-plugins",
    }

    # Specify a CSS selector for main content (use developer tools to find this)
    main_content_selector = "main"  # Example: Use <main> tag or customize as needed

    # Perform scraping and save the results to 'aggregated_data.pkl'
    extract_and_store(site_urls, 'aggregated_data.pkl', main_content_selector)
