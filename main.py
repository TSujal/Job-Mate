import streamlit as st
from Agents.agent1_JD import query_and_scrape_agent
from Agents.agent2_cover_letter import resume_analyzer_agent
from Agents.agent3_resume_tailor import get_resume_summary, get_skill_improvement, get_ats_match, get_resume_optimizations
from workflow.graph_workflow import create_workflow
from utils.pdf_utils import generate_pdf, timestamped_msg, extract_pdf_text
from datetime import datetime

def main():
    st.set_page_config(page_title="Cover Letter & Resume Tailor", layout="centered")
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #e1f5fe;
        }
        .stButton>button {
            background-color: #0056b3;
            color: white;
            border-radius: 5px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #1C2526;
            color: white;
        }
        .stTextInput>div>input {
            background-color: #e6f3ff;
            color: #333333;
            border: 1px solid #007bff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("🧠 AI Application Assistant")

    # Session state initialization
    for key in ["groq_api_key", "latest_state", "cover_letters"]:
        if key not in st.session_state:
            st.session_state[key] = [] if key == "cover_letters" else None

    key = st.text_input("**🔑 Groq API Key**", type="password", value=st.session_state.groq_api_key)
    if not key:
        st.warning("Please provide a valid Groq API key.")
        st.stop()
    st.session_state.groq_api_key = key

    query = st.text_input("**💼 What do you need help with?**")
    url = st.text_input("**🔗 Job Posting URL**")
    linkedin_input = st.text_area("**🌐 LinkedIn URL (optional)**")
    portfolio_input = st.text_area("**🌐 Portfolio URL (optional)**")
    resume_file = st.file_uploader("**📋 Resume (PDF)**", type=["pdf"], key="resume")
    last_cl_file = st.file_uploader("**📜 Last Cover Letter (PDF/TXT)**", type=["pdf", "txt"], key="last_cl")

    st.subheader("🔍 Resume & Cover Letter Options")

    if st.button("📄 Tell Me About My Resume"):
        if not resume_file or not query:
            st.warning("Please upload a resume and provide a query.")
        else:
            with st.spinner("🔧 Analyzing your resume..."):
                summary = get_resume_summary(resume_file, query)
                st.write(summary)

    if st.button("🔧 How Can I Improve My Skills?"):
        if not resume_file or not query:
            st.warning("Please upload a resume and provide a query.")
        else:
            with st.spinner("🔧 Analyzing skill improvements..."):
                improvements = get_skill_improvement(resume_file, query)
                st.write(improvements)

    if st.button("⭐ ATS Percentage Match"):
        if not resume_file or not url:
            st.warning("Please upload a resume and provide a job posting URL.")
        else:
            with st.spinner("🔧 Fetching job description and analyzing ATS match..."):
                init = {
                    "query": query or "Unknown Job Title",
                    "url": url,
                    "additional_links": [linkedin_input, portfolio_input],
                    "job_description": "",
                    "extra_web_content": "",
                    "resume": "",
                    "last_cover_letter": "",
                    "cover_letter": "",
                    "feedback": "",
                    "ats_score": "",
                    "skill_improvements": "",
                    "resume_optimizations": "",
                    "messages": []
                }
                state = query_and_scrape_agent(init)
                job_description = state["job_description"]
                if not job_description:
                    st.warning("Failed to fetch job description from the provided URL.")
                else:
                    ats_match = get_ats_match(resume_file, job_description)
                    st.write(ats_match)

    if st.button("🎯 Quick Key Resume Improvement"):
        if not resume_file or not query:
            st.warning("Please upload a resume and provide a query.")
        else:
            with st.spinner("🔧 Analyzing resume optimizations..."):
                optimizations = get_resume_optimizations(resume_file, query)
                st.write(optimizations)

    # Generate Cover Letter
    if st.button("🚀 Generate Cover Letter"):
        if not (query and url and resume_file and last_cl_file):
            st.warning("Please fill all fields.")
        else:
            resume_text = extract_pdf_text(resume_file)
            last_text = (
                extract_pdf_text(last_cl_file)
                if last_cl_file.name.endswith(".pdf")
                else last_cl_file.read().decode()
            )
            init = {
                "query": query,
                "url": url,
                "additional_links": [linkedin_input, portfolio_input],
                "job_description": "",
                "extra_web_content": "",
                "resume": resume_text,
                "last_cover_letter": last_text,
                "cover_letter": "",
                "feedback": "",
                "ats_score": "",
                "skill_improvements": "",
                "resume_optimizations": "",
                "messages": []
            }

            try:
                with st.spinner("🔧 Generating cover letter..."):
                    app = create_workflow()
                    state = app.invoke(init)
                    cl_text = state.get("cover_letter", "")
                    if cl_text:
                        st.session_state.cover_letters.append({"text": cl_text, "state": state})
            except Exception as e:
                st.error(f"Error generating cover letter: {str(e)}")

    # Show all generated cover letters + feedback blocks
    for i, cl in enumerate(st.session_state.cover_letters):
        st.subheader(f"📬 Cover Letter #{i + 1}")
        st.write(cl["text"])
        st.download_button(
            label="📄 Download PDF",
            data=generate_pdf(cl["text"]),
            file_name=f"cover_letter_{i+1}.pdf",
            mime="application/pdf",
            key=f"download_{i}"
        )

        with st.form(f"feedback_form_{i}"):
            fb = st.text_area("✍️ Provide feedback for revision:")
            submitted = st.form_submit_button("♻️ Revise This Cover Letter")
            if submitted:
                if not fb:
                    st.warning("Please enter feedback.")
                else:
                    try:
                        with st.spinner("🔁 Revising..."):
                            upd = cl["state"].copy()
                            upd["feedback"] = fb
                            upd["messages"] = upd.get("messages", []) + [timestamped_msg(content=f"[User Feedback] {fb}")]
                            app = create_workflow()
                            revised_state = app.invoke(upd)
                            revised_cl = revised_state.get("cover_letter", "")
                            if revised_cl:
                                st.session_state.cover_letters.append({"text": revised_cl, "state": revised_state})
                                st.rerun()
                    except Exception as e:
                        st.error(f"Error revising cover letter: {str(e)}")

    # Agent log
    if st.session_state.cover_letters:
        last_state = st.session_state.cover_letters[-1]["state"]
        if last_state and last_state.get("messages", []):
            with st.expander("📜 View Agent Communication Log"):
                for msg in last_state["messages"]:
                    st.markdown(f"- {msg.content}")

if __name__ == "__main__":
    main()
