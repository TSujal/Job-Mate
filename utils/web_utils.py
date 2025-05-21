import re
import requests
from bs4 import BeautifulSoup

def extract_company_name(url: str, job_description: str) -> str:
    m = re.search(r'https?://(?:www\.)?([a-zA-Z0-9-]+)', url)
    if m:
        return m.group(1).title()
    for kw in ["at", "with", "in", "by"]:
        if kw in job_description.lower():
            return job_description.split(kw)[0].strip().title()
    return "Hiring Manager"

def scrape_webpage_text(url: str) -> str:
    try:
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        texts = soup.find_all(string=True)
        visible = filter(lambda t: t.parent.name not in ['style','script','head','meta'], texts)
        return " ".join(t.strip() for t in visible if t.strip())
    except:
        return ""
