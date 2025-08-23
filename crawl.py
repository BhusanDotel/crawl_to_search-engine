from selenium import webdriver
from multiprocessing import Pool, cpu_count
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


from persists_data import get_links_from_db, save_to_db, update_to_db, update_to_db

# Open your target page
BASE_URL="https://pureportal.coventry.ac.uk/en/organisations/fbl-school-of-economics-finance-and-accounting/publications/"


def safe_text(driver, finder, by, selector):
    try:
        # result = driver[finder](by, selector)
        result = getattr(driver, finder)(by, selector)
        return result
    except NoSuchElementException:
        return None

#=============== HandleCookie=====================
def cookie_handler(driver):
    try:
        accept_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        accept_btn.click()
        print("Accepted Cookies")
    except:
        print("No cookie popup found")


#=============== Scrape papers list =====================
def scrape_paper_list(driver, url, page):
    print("----"*10)

    paper_list=[]
    print("page",page)
    driver.get(url)
    cookie_handler(driver)

    _results = safe_text(driver, "find_elements", By.CSS_SELECTOR, "h3.title a")
    result = _results if len(_results) > 0 else []

    for r in result:
        link = r.get_attribute("href")
        paper_list.append(link)
        save_to_db(link)

    next_page_btn = safe_text(driver, "find_elements", By.CSS_SELECTOR, "nav.pages ul li.next a")
    next_page_link = next_page_btn[0].get_attribute("href") if next_page_btn else ""

    if next_page_link != "":
        page += 1
        scrape_paper_list(driver, next_page_link, page)
    return paper_list


#=============== Scrape paper detail =====================
def scrape_paper_detail(driver, url):
    driver.get(url)
    cookie_handler(driver)

    authors = []

    _title = safe_text(driver, "find_element", By.CSS_SELECTOR, "h1 span")
    title = _title.text if _title else ""

    _abstract = safe_text(driver, "find_element", By.CSS_SELECTOR, "div.rendering_contributiontojournal_abstractportal div.textblock")
    abstract = _abstract.text if _abstract else ""

    _language = safe_text(driver, "find_element", By.CSS_SELECTOR, "table.properties tbody tr.language td")
    language = _language.text if _language else ""

    _published = safe_text(driver, "find_element", By.CSS_SELECTOR, "table.properties tbody tr.status td span.date")
    published = _published.text if _published else ""

    author_container = safe_text(driver, "find_element", By.CSS_SELECTOR, "div.rendering_contributiontojournal_associatespersonsclassifiedportal p.persons")

    links = safe_text(author_container, "find_elements", By.TAG_NAME, "a") if author_container else []
    for link in links:
        authors.append({
            "name": link.text.strip(),
            "link": link.get_attribute("href")
        })

    # Get remaining text (authors without links)
    text_nodes = author_container.text if author_container else ""
    # Already contains all names including linked ones, so remove linked ones
    linked_names = [a["name"] for a in authors]

    # Split by comma
    for name in text_nodes.split(","):
        clean_name = name.strip().strip('"')
        if clean_name and clean_name not in linked_names:
            authors.append({"name": clean_name, "link": None})

    return {
        "title": title,
        "link": url,
        "abstract": abstract,
        "language": language,
        "published": published,
        "authors": authors
    }


#=============== Process Link =====================
def process_link(link):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    detail = scrape_paper_detail(driver, link)
    update_to_db(detail)
    driver.quit()
    return link

#=============== Start Crawl =====================
def start_crawl():
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # scrape_paper_list(driver, BASE_URL, 1)
    links = get_links_from_db()
    print(f"Total links to process: {len(links)}")
    # total = len(links)

    # workers = min(10, cpu_count())  # 5 parallel browsers

    # with Pool(workers) as pool:
    #     for i, _ in enumerate(pool.imap_unordered(process_link, links), 1):
    #         print(f"Processed {i}/{total}")

if __name__ == "__main__":
    start_crawl() 