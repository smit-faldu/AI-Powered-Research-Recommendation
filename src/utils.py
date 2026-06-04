import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchResults
from tenacity import retry, stop_after_attempt, wait_exponential
import dotenv
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import datetime

dotenv.load_dotenv()

def log_scraped_data(source: str, identifier: str, content: str):
    """Prints and saves scraped/search data to a separate log file for monitoring."""
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file_path = os.path.join(log_dir, "scraped_data.log")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    divider = "=" * 80
    log_entry = (
        f"\n{divider}\n"
        f"[{timestamp}] SOURCE: {source}\n"
        f"TARGET/QUERY: {identifier}\n"
        f"{divider}\n"
        f"{content}\n"
        f"{divider}\n"
    )
    
    # 1. Print to console/stdout
    print(log_entry, flush=True)
    
    # 2. Append to the separate log file
    try:
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Failed to write to log file: {str(e)}", flush=True)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def execute_robust_search(search_tool: DuckDuckGoSearchResults, query: str) -> str:
    """Executes structural web parsing with automated rate limit handling layers."""
    result = search_tool.invoke(query)
    log_scraped_data("DuckDuckGo Search Tool", query, result)
    return result

def safe_llm_invoke(llm, prompt: str) -> str:
    """Safely invokes structural models."""
    return llm.invoke(prompt).content

def get_llm(temperature: float = 0.1) -> ChatGoogleGenerativeAI:
    """Returns the gemini-flash-latest model as configured."""
    return ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=temperature)


def crawl_website_text(url: str, max_chars: int = 8000) -> tuple[str, BeautifulSoup | None]:
    """Fetches web page content, strips styles/scripts/nav, and returns cleaned text."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    try:
        response = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove navigation, headers, footers, scripts, and styles to get core content
        for element in soup(["script", "style", "noscript", "header", "footer", "nav", "svg", "iframe"]):
            element.decompose()
            
        text = soup.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)
        
        result_text = clean_text[:max_chars]
        log_scraped_data("Web Crawler Success", url, result_text)
        return result_text, soup
    except Exception as e:
        error_msg = f"Crawl failed for {url}: {str(e)}"
        log_scraped_data("Web Crawler Failure", url, error_msg)
        return error_msg, None

def find_about_page_url(soup: BeautifulSoup, base_url: str) -> str | None:
    """Identifies an About Us or Company Profile page from links on the homepage."""
    if not soup:
        return None
        
    about_keywords = ["about", "who we are", "company profile", "profile", "our story", "overview", "history", "who-we-are"]
    parsed_base = urllib.parse.urlparse(base_url)
    
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text().strip().lower()
        
        is_about = any(kw in text for kw in about_keywords) or any(kw in href.lower() for kw in about_keywords)
        
        if is_about:
            abs_url = urllib.parse.urljoin(base_url, href)
            
            # Avoid crawling the homepage again if it is just an anchor link
            abs_url_clean = abs_url.split('#')[0]
            base_url_clean = base_url.split('#')[0]
            if abs_url_clean == base_url_clean:
                continue
                
            parsed_abs = urllib.parse.urlparse(abs_url)
            if parsed_abs.scheme in ("http", "https"):
                base_domain = parsed_base.netloc.replace("www.", "")
                abs_domain = parsed_abs.netloc.replace("www.", "")
                if base_domain == abs_domain or abs_domain.endswith("." + base_domain) or base_domain.endswith("." + abs_domain):
                    return abs_url
                    
    return None

