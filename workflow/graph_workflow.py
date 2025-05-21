from langgraph.graph import StateGraph, END
from Agents.agent1_JD import query_and_scrape_agent
from Agents.agent2_cover_letter import resume_analyzer_agent
from Agents.agent3_resume_tailor import resume_tailor_agent
from typing import TypedDict, List, Annotated
import operator
from utils.pdf_utils import timestamped_msg

class AgentState(TypedDict):
    query: str
    url: str
    additional_links: List[str]
    job_description: str
    resume: str
    extra_web_content: str
    last_cover_letter: str
    cover_letter: str
    feedback: str
    ats_score: str
    skill_improvements: str
    resume_optimizations: str
    messages: Annotated[List[timestamped_msg], operator.add]

def create_workflow():
    wf = StateGraph(AgentState)
    wf.add_node("query_and_scrape", query_and_scrape_agent)
    wf.add_node("resume_analyzer", resume_analyzer_agent)
    wf.add_node("resume_tailor", resume_tailor_agent)
    wf.set_entry_point("query_and_scrape")
    wf.add_edge("query_and_scrape", "resume_analyzer")
    wf.add_edge("resume_analyzer", "resume_tailor")
    wf.add_edge("resume_tailor", END)
    return wf.compile()