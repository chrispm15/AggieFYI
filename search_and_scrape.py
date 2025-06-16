# search_and_scrape.py
import os
import requests
from bs4 import BeautifulSoup
import openai
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")


def run_search_and_summarize(user_msg):
    query = f"Texas A&M 2025{user_msg}"
    encoded_query = quote_plus(query)
    url = f"https://api.search.brave.com/res/v1/web/search?q={encoded_query}&count=6"

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }

    print(f"[INFO] Searching Brave for: {query}")
    print(f"[DEBUG] Search URL: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        raw_results = response.json().get("web", {}).get("results", [])
    except Exception as e:
        print(f"[ERROR] Search API error: {str(e)}")
        return [f"Search error: {str(e)}"]

    urls = [r.get("url") for r in raw_results if r.get("url")]
    print(f"[INFO] Retrieved {len(urls)} URLs from Brave")

    summaries = []
    for url in urls:
        text = scrape_text(url)
        if text:
            summary = summarize(text, user_msg)
            if summary:
                summaries.append(f"- {summary.strip()} (Source: {url})")

    return summaries or ["No useful information found."]


def scrape_text(url):
    try:
        print(f"[INFO] Scraping: {url}")
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove irrelevant tags
        for tag in soup(["script", "style", "header", "footer", "nav", "aside", "form"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title else ""
        paragraphs = soup.find_all("p")
        content = "\n".join(p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 40)

        clean_text = f"{title}\n\n{content[:2000]}"
        return clean_text
    except Exception as e:
        print(f"[ERROR] Failed to scrape {url}: {str(e)}")
        return ""


def summarize(text, question):
    prompt = f"Summarize this to help answer: '{question}'\n\n{text[:8000]}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You summarize news and sports content for Texas A&M fans."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] Failed to summarize: {str(e)}")
        return "[Summarization error]"
