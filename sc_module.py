from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import pickle
import re


def setup_driver():
    """
    Configures and initializes the Selenium WebDriver.

    Returns:
        webdriver.Chrome: An instance of Chrome WebDriver.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service("path_to_chromedriver")  # Replace with the path to your ChromeDriver
    return webdriver.Chrome(service=service, options=chrome_options)


def clean_webpage_content(webpage_content):
    """
    Cleans raw webpage content by removing extra whitespace.

    Args:
        webpage_content (str): Raw content extracted from the webpage.

    Returns:
        str: Cleaned content.
    """
    # Remove extra whitespace
    return ' '.join(webpage_content.split())


def extract_links(driver, base_url):
    """
    Extracts all links from the current webpage.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        base_url (str): The base URL for resolving relative links.

    Returns:
        dict: A dictionary of links where keys are the relative paths and values are absolute URLs.
    """
    links = {}
    elements = driver.find_elements(By.TAG_NAME, "a")
    for element in elements:
        href = element.get_attribute("href")
        if href and href.startswith("http"):
            links[href] = href
    return links


def scrape_website(url, label, hover_selector=None):
    """
    Scrapes the specified URL and captures dynamic content.

    Args:
        url (str): The URL to scrape.
        label (str): A label for the section being scraped.
        hover_selector (str): CSS selector to hover over elements for dynamic content (optional).

    Returns:
        tuple: Cleaned content and extracted links from the webpage.
    """
    print(f"Scraping {label} ({url})...")
    driver = setup_driver()

    try:
        driver.get(url)
        time.sleep(3)  # Allow time for the page to load

        # Perform hover actions if a hover selector is provided
        if hover_selector:
            action = ActionChains(driver)
            hover_elements = driver.find_elements(By.CSS_SELECTOR, hover_selector)
            for element in hover_elements:
                action.move_to_element(element).perform()
                time.sleep(1)  # Allow dynamic content to load

        # Extract visible text from the webpage
        raw_content = driver.find_element(By.TAG_NAME, "body").text

        # Extract all links
        links_list = extract_links(driver, base_url=url)

        # Clean raw content
        cleaned_content = clean_webpage_content(raw_content)

        print(f"Links Found on {label}: {len(links_list)}")
        return cleaned_content, links_list

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None, None

    finally:
        driver.quit()


def scrape_and_save(website_urls, output_file, hover_selector=None):
    """
    Scrapes multiple URLs and saves the results to a file.

    Args:
        website_urls (dict): Dictionary of labels and corresponding URLs to scrape.
        output_file (str): File path to save the scraped data.
        hover_selector (str): CSS selector to hover over elements for dynamic content (optional).
    """
    all_data = {}

    for label, url in website_urls.items():
        cleaned_content, links_list = scrape_website(url, label, hover_selector)
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
    # Define the website URLs to scrape
    website_urls = {
        "Home": "https://botpenguin.com/",
        "Pricing": "https://botpenguin.com/chatbot-pricing",
        "Partners": "https://botpenguin.com/partners/chatbot-affiliate-program",
        "Ecommerce Industry": "https://botpenguin.com/chatbot-industry/ecommerce",
        "Solutions": "https://botpenguin.com/solutions/custom-chatgpt-plugins",
    }

    # Specify a hover selector for dynamic content (optional)
    hover_selector = ".hover-target"  # Replace with the actual CSS selector for hover elements

    # Scrape the website URLs and save the data to 'data.pkl'
    scrape_and_save(website_urls, 'data.pkl', hover_selector)
