from utils.model_utils import get_groq_llm
from langchain_core.messages import HumanMessage
from utils.web_utils import extract_company_name

def timestamped_msg(content: str) -> HumanMessage:
    from datetime import datetime
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    return HumanMessage(content=f"{ts} {content}")

def resume_analyzer_agent(state):
    if not state["job_description"] or not state["resume"]:
        return {**state,
                "cover_letter": "",
                "messages": state["messages"] + [timestamped_msg(content="[Agent2] ❌ Missing job description or resume")]}

    # Extract company and generate prompt
    company = extract_company_name(state["url"], state["job_description"])
    prompt = f"""
    You are a professional cover letter writer.

    Your task is to create a personalized, confident-sounding cover letter showcasing the candidate's fit.

    --- CONTEXT ---
    Job Title: {state['query']}
    Company Name: {company}

    --- JOB DESCRIPTION ---
    {state['job_description'][:2000]}

    --- RESUME ---
    {state['resume'][:2000]}

    --- EXTRA WEB CONTENT ---
    {state['extra_web_content'][:2000]}

    --- LAST COVER LETTER ---
    {state['last_cover_letter'][:1000]}

    --- USER FEEDBACK ---
    {state['feedback']}

    --- INSTRUCTIONS ---
    Begin with "Dear Hiring Manager," and mention relevant experience and projects.
    Align skills and responsibilities to the job description.
    Incorporate the user's feedback wherever applicable.
    """
    
    # Use the model to generate or revise the cover letter
    llm = get_groq_llm(agent="agent2")
    if not llm:
        return {**state, 
                "cover_letter": "",
                "messages": state["messages"] + [timestamped_msg(content="[Agent2] ❌ LLM unavailable")]}

    try:
        cl = llm.invoke(prompt).content
    except Exception as e:
        return {**state, 
                "cover_letter": "",
                "messages": state["messages"] + [timestamped_msg(content=f"[Agent2] ❌ {e}")]}
    
    # Return the updated state with the new cover letter and messages
    return {**state, 
            "cover_letter": cl, 
            "messages": state["messages"] + [timestamped_msg(content="[Agent2] ✅ Cover letter generated/revised")]}