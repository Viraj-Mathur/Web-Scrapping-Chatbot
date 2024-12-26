# scraper_module.py

import requests
from bs4 import BeautifulSoup
import pickle
import re


def clean_webpage_content(webpage_content):
    """
    Cleans the raw webpage content by removing JavaScript, HTML tags,
    and extra whitespace.
    """
    # Remove JavaScript code
    webpage_content = re.sub(
        r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',
        '',
        webpage_content,
        flags=re.DOTALL
    )
    # Remove CSS styles
    webpage_content = re.sub(
        r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>',
        '',
        webpage_content,
        flags=re.DOTALL
    )
    # Remove HTML tags
    webpage_content = re.sub(r'<[^>]+>', '', webpage_content)
    # Remove extra whitespace
    webpage_content = ' '.join(webpage_content.split())
    return webpage_content


def extract_links(website_html, base_url):
    """
    Extracts all unique links from the website HTML and returns a dictionary
    mapping relative paths to full URLs.

    Args:
        website_html (str): The raw HTML content of the webpage.
        base_url (str): The base URL for resolving relative links.

    Returns:
        dict: A dictionary mapping relative paths to absolute URLs.
    """
    soup = BeautifulSoup(website_html, 'html.parser')
    links = {}
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        # Skip empty and invalid hrefs
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue
        # Resolve relative URLs to absolute
        if href.startswith('/'):
            links[href] = f'{base_url.rstrip("/")}{href}'
        elif href.startswith('http'):
            links[href] = href
    return links


def scrape_website(url, label, content_selector=None):
    """
    Scrapes the specified URL, extracts and cleans content, and finds all links.

    Args:
        url (str): The URL to scrape.
        label (str): A label for the section being scraped.
        content_selector (str): CSS selector to target the main content (optional).

    Returns:
        tuple: A tuple containing the cleaned content and a list of extracted links.
    """
    print(f"Scraping {label} ({url})...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error making request to {url}: {e}")
        return None, None

    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # If a specific content selector is provided, use it
    if content_selector:
        target_element = soup.select_one(content_selector)
        if target_element:
            raw_content = target_element.get_text()
        else:
            print(f"Content selector '{content_selector}' not found on {label}.")
            raw_content = soup.get_text()
    else:
        # Default to the full page text
        raw_content = soup.get_text()

    # Extract all links
    links_list = extract_links(soup.prettify(), url)
    print(f"Links Found on {label}: {len(links_list)}")

    # Clean raw text content
    cleaned_content = clean_webpage_content(raw_content)

    return cleaned_content, links_list


def scrape_and_save(website_urls, output_file, content_selector=None):
    """
    Scrapes multiple URLs and saves the results to a file in a structured format.

    Args:
        website_urls (dict): A dictionary of labels and their corresponding URLs to scrape.
        output_file (str): The file to save the scraped data.
        content_selector (str): CSS selector to target the main content of the webpage (optional).
    """
    all_data = {}

    for label, url in website_urls.items():
        cleaned_content, links_list = scrape_website(url, label, content_selector)
        if cleaned_content:
            all_data[label] = {
                'context': cleaned_content,
                'links': links_list
            }
            print(f"Data extracted for {label}.")

    # Save all data to a pickle file
    with open(output_file, 'wb') as file:
        pickle.dump(all_data, file)
    print(f"All data saved to {output_file}.")


if __name__ == '__main__':
    # Define the extracted URLs
    website_urls = {
        "Home": "https://botpenguin.com/",
        "Pricing": "https://botpenguin.com/chatbot-pricing",
        "Partners": "https://botpenguin.com/partners/chatbot-affiliate-program",
        "Ecommerce Industry": "https://botpenguin.com/chatbot-industry/ecommerce",
        "Solutions": "https://botpenguin.com/solutions/custom-chatgpt-plugins",
    }

    # Specify a CSS selector for the main content (if applicable)
    # Adjust the selector based on the structure of the website you're scraping
    content_selector = "main"  # Example: Use the <main> tag as a target

    # Scrape the URLs and save the results to 'data.pkl'
    scrape_and_save(website_urls, 'data.pkl', content_selector)
