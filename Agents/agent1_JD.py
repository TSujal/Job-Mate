import requests
from bs4 import BeautifulSoup
import re
from utils.web_utils import extract_company_name, scrape_webpage_text
from utils.model_utils import get_groq_llm
from langchain_core.messages import HumanMessage

def timestamped_msg(content: str) -> HumanMessage:
    from datetime import datetime
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    return HumanMessage(content=f"{ts} {content}")

def query_and_scrape_agent(state):
    try:
        r = requests.get(state["url"], headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        html = r.text
    except Exception as e:
        return {**state,
                "job_description":"",
                "messages": state["messages"] + [timestamped_msg(content=f"[Agent1] ❌ {e}")]}

    soup = BeautifulSoup(html, "html.parser")
    jd = " ".join(elem.get_text(strip=True)
                  for elem in soup.select(".job-description, .description, [class*='desc']"))
    jd = re.sub(r'\s+',' ', jd).strip()

    extra = ""
    for link in state["additional_links"]:
        txt = scrape_webpage_text(link)
        if txt:
            extra += txt[:2000] + "\n"

    company = extract_company_name(state["url"], jd)
    msgs = state["messages"] + [
        timestamped_msg(content=f"[Agent1] ✅ Job snippet: {jd[:200]}..."),
        timestamped_msg(content=f"[Agent1] ✅ Scraped {len(state['additional_links'])} extra URLs"),
        timestamped_msg(content=f"[Agent1 ➡ Agent2] Company: {company}")
    ]
    return {**state, "job_description":jd, "extra_web_content":extra, "messages":msgs}
