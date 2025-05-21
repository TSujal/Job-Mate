import os
import io
import base64
import pdf2image
import google.generativeai as genai
from dotenv import load_dotenv
from utils.model_utils import get_gemini_response
from utils.pdf_utils import timestamped_msg
from langchain_core.messages import HumanMessage
from io import BytesIO

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_PRO_API_KEY"))

# Define PROMPTS
PROMPTS = {
    "summary": """
    You are a senior Human Resources Manager with extensive experience hiring for Data Science, AI, Machine learning, Deep learning and Data Analyst roles.
    Your task is to evaluate the candidate's resume based on the provided job description.
    Please provide:
    1. A summary of the candidate’s overall profile.
    2. How well the resume aligns with the role requirements.
    3. A breakdown of key strengths and notable skills relevant to the job.
    4. Any gaps or mismatches between the resume and the job expectations.
    Your tone should be professional, insightful, and HR-focused.
    """,
    "improvement": """
    You are a Strategic Career Advisor with 15+ years of expertise in Data Science, AI, Machine Learning, Deep Learning, and Data Analytics talent development and recruitment.
    EVALUATION OBJECTIVE:
    Analyze the resume against the job description to identify strategic improvement opportunities that will significantly enhance the candidate's qualifications and competitiveness for this specific role and similar positions in the field.
    COMPREHENSIVE ANALYSIS FRAMEWORK:
    1. TECHNICAL SKILL GAP ANALYSIS:
       - Identify critical technical skills mentioned in the job description that are:
         a) Missing entirely from the resume
         b) Present but underdeveloped
         c) Present but not demonstrated effectively
       - For each gap, provide:
         * 🔍 Gap Identified: Specific skill or technology requirement
         * 📊 Criticality: [Essential/Important/Beneficial] to securing this role
         * 🎯 Acquisition Path: Specific resources, courses, certifications, or projects (with links where possible)
         * ⏱️ Estimated Timeline: Realistic timeframe to develop sufficient proficiency
         * 💼 Application Strategy: How to demonstrate this skill before fully acquiring it (projects, contributions)
    2. EXPERIENCE ENHANCEMENT OPPORTUNITIES:
       - Identify areas where candidate's experience could be strengthened to match job requirements:
         * 🔍 Experience Gap: Specific type of experience required
         * 💡 Bridge Strategy: How to gain relevant experience through:
           - Side projects (with specific project suggestions)
           - Open source contributions (with recommended repositories)
           - Volunteer work or pro-bono consulting
           - Learning projects that demonstrate applicable skills
         * 🌟 Transferable Experience: How to better leverage existing experience to address this gap
         * 📝 Documentation Strategy: How to effectively showcase new experiences on resume
    3. EDUCATION & CERTIFICATION ROADMAP:
       - Evaluate educational requirements against candidate's background:
         * 🔍 Educational Gap: Specific degree, specialization, or knowledge area
         * 📜 Certification Opportunities: Specific certifications that would strengthen candidacy
         * 🎓 Alternative Credentials: Other forms of recognized credentials
         * 🔄 Continuous Learning Path: Targeted resources for ongoing professional development
    4. TOOLS & TECHNOLOGY ADVANCEMENT:
       - Identify specific tools mentioned in job description:
         * 🔍 Missing Tool/Technology: Tool/platform mentioned in job requirements
         * 💻 Learning Resources: Specific tutorials, courses, documentation
         * 🛠️ Practice Opportunity: Concrete project ideas to demonstrate proficiency
         * 🏆 Proficiency Indicator: How to demonstrate mastery
    5. SOFT SKILLS & PROFESSIONAL DEVELOPMENT:
       - Identify key soft skills emphasized in the job description:
         * 🔍 Soft Skill Gap: Communication, leadership, teamwork, etc.
         * 🌱 Development Strategy: Specific steps to strengthen this skill
         * 📈 Demonstration Method: How to evidence this skill on resume/portfolio
    6. INDUSTRY KNOWLEDGE ENHANCEMENT:
       - Identify sector-specific knowledge requirements:
         * 🔍 Knowledge Gap: Industry-specific knowledge area
         * 📚 Knowledge Sources: Industry publications, events, communities
         * 🗣️ Networking Strategy: Key connections to develop in this knowledge area
    7. STRATEGIC PRIORITIZATION:
       - Provide a prioritized improvement roadmap with:
         * 🥇 Immediate Actions (0-3 months)
         * 🥈 Medium-term Development (3-6 months)
         * 🥉 Long-term Growth (6+ months)
    8. COMPETITIVE DIFFERENTIATION STRATEGY:
       - Recommend:
         * 🔍 Unique Selling Proposition: How candidate can stand out
         * 🌟 Specialization Opportunity: Niche area for expertise
         * 🏆 Portfolio Development: Specific projects for unique capabilities
    RESPONSE FORMAT:
    - Begin with a succinct overview of the candidate's current position
    - Structure analysis using the 8 categories above
    - Conclude with a prioritized 30-60-90 day improvement plan
    """,
    "match": """
    You are a calibrated ATS scoring system designed to evaluate resume and job description alignment for roles in Data Science, AI, Machine Learning, Deep Learning, and Data Analytics.
    SCORING PHILOSOPHY:
    - Use the full 0–100% range.
    - Excellent matches (90%+) uncommon but achievable.
    - Most qualified resumes score 70–85%.
    - Moderately qualified resumes score 50–70%.
    SCORING COMPONENTS:
    1. Technical Skills Match (40%)
       - Score each skill: Strong (100%), Moderate (70%), Mentioned (40%), Absent (0%)
    2. Keyword Overlap (25%)
       - Score: Present in projects (100%), skills section (75%), partial match (50%)
    3. Relevant Experience (20%)
       - Consider title, industry, projects, recency
    4. Education & Certifications (10%)
       - Exact degree (90–100), related field (60–80)
    5. Soft Skills & Industry Fit (5%)
       - Credit contextual demonstration
    OUTPUT FORMAT:
    1. Final Match Score: X%
       - Classification: Outstanding / Strong / Moderate / Fair / Weak Match
    2. Component Breakdown:
       - Technical Skills: X/100
       - Keywords: X/100
       - Experience: X/100
       - Education: X/100
       - Soft Skills: X/100
    3. Key Strengths:
       ✅ [Top 3 aligned elements]
    4. Gaps to Address:
       ❌ [Top misaligned or missing elements]
    5. Suggestions:
       🚀 [Specific, non-generic suggestions]
    Ensure balanced evaluation, reflecting real hiring team views.
    """,
    "optimize": """
    You are an expert Resume Optimization Specialist with 10+ years of experience in ATS systems for Data Science, AI, Machine Learning, Deep Learning, and Data Analytics roles.
    TASK OVERVIEW:
    Analyze resume against job description to improve ATS ranking without misrepresentation.
    ANALYSIS PROCESS:
    1. Extract keywords, skills, tools from job description
    2. Map against resume content
    3. Identify optimization opportunities:
       a) Phrasing improvements
       b) Keyword alignment
       c) Technical terminology
       d) Achievement framing
       e) ATS-friendly formatting
    OPTIMIZATION RECOMMENDATIONS:
    1. PHRASING IMPROVEMENTS:
       ✅ Current: "{phrase}"
       🔁 Optimized: "{improved}"
       💬 Rationale: Why it improves ATS
       📈 Impact: [High/Medium/Low]
    2. MISSING KEYWORDS:
       ❌ Missing: "{keyword}"
       💡 Integration: "{how to incorporate}"
       🔍 Location: Where to add
    3. TECHNICAL SKILL OPTIMIZATION:
       ✅ Current: "{skill}"
       🔁 Enhanced: "{improved}"
       💬 Rationale: Better alignment
    4. ACHIEVEMENT TRANSFORMATION:
       ✅ Current: "{statement}"
       🔁 Achievement: "{quantified}"
       💬 Rationale: Demonstrates impact
    5. STRUCTURAL RECOMMENDATIONS:
       - Optimal section ordering
       - Bullet point structure
       - Formatting for ATS
    6. PRIORITY OPTIMIZATIONS:
       - Top 3-5 changes for highest impact
    GUIDELINES:
    - Never invent experience
    - Focus on honest reframing
    - Prioritize high-impact changes
    - Be specific, maintain factual accuracy
    FORMAT:
    - Assess current ATS-friendliness
    - Provide recommendations by category
    - Summarize 3-5 highest-impact changes
    """
}

def input_pdf_setup(uploaded_file=None, resume_text=None):
    """
    Prepare input for Gemini model, either from PDF or text.
    """
    try:
        if uploaded_file:
            try:
                images = pdf2image.convert_from_bytes(uploaded_file.read())
                first_page = images[0]
                img_byte_arr = io.BytesIO()
                first_page.save(img_byte_arr, format="JPEG")
                img_byte_arr = img_byte_arr.getvalue()
                return [{
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()
                }]
            except Exception as e:
                return f"Error processing PDF: {str(e)}. Please ensure the PDF is valid and poppler is installed."
        elif resume_text:
            return [{
                "mime_type": "text/plain",
                "data": base64.b64encode(resume_text.encode()).decode()
            }]
        else:
            return "No file or text provided."
    except Exception as e:
        return f"Error processing input: {str(e)}"

def get_resume_summary(uploaded_file, job_description):
    """
    Generate a resume summary for direct UI use.
    """
    context_data = input_pdf_setup(uploaded_file=uploaded_file)
    if isinstance(context_data, str):
        return context_data  # Return error message
    prompt = f"{PROMPTS['summary']}\n\nJob Description:\n{job_description}"
    return get_gemini_response(prompt, context_data[0])

def get_skill_improvement(uploaded_file, job_description):
    """
    Generate skill improvement suggestions for direct UI use.
    """
    context_data = input_pdf_setup(uploaded_file=uploaded_file)
    if isinstance(context_data, str):
        return context_data  # Return error message
    prompt = f"{PROMPTS['improvement']}\n\nJob Description:\n{job_description}"
    return get_gemini_response(prompt, context_data[0])

def get_ats_match(uploaded_file, job_description):
    """
    Generate ATS match score for direct UI use.
    """
    context_data = input_pdf_setup(uploaded_file=uploaded_file)
    if isinstance(context_data, str):
        return context_data  # Return error message
    prompt = f"{PROMPTS['match']}\n\nJob Description:\n{job_description}"
    return get_gemini_response(prompt, context_data[0])

def get_resume_optimizations(uploaded_file, job_description):
    """
    Generate resume optimization recommendations for direct UI use.
    """
    context_data = input_pdf_setup(uploaded_file=uploaded_file)
    if isinstance(context_data, str):
        return context_data  # Return error message
    prompt = f"{PROMPTS['optimize']}\n\nJob Description:\n{job_description}"
    return get_gemini_response(prompt, context_data[0])

def resume_tailor_agent(state):
    """
    Agent 3: Analyzes resume against job description, provides ATS score, skill improvements, and resume optimizations for workflow.
    """
    if not state["job_description"] or not state["resume"]:
        return {
            **state,
            "ats_score": "",
            "skill_improvements": "",
            "resume_optimizations": "",
            "messages": state["messages"] + [timestamped_msg(content="[Agent3] ❌ Missing job description or resume")]
        }

    try:
        # Use resume text from state
        context_data = input_pdf_setup(resume_text=state["resume"])
        if isinstance(context_data, str):
            return {
                **state,
                "ats_score": "",
                "skill_improvements": "",
                "resume_optimizations": "",
                "messages": state["messages"] + [timestamped_msg(content=f"[Agent3] ❌ {context_data}")]
            }

        # Get ATS match
        ats_prompt = f"{PROMPTS['match']}\n\nJob Description:\n{state['job_description']}"
        ats_score = get_gemini_response(ats_prompt, context_data[0])

        # Get skill improvements
        improvement_prompt = f"{PROMPTS['improvement']}\n\nJob Description:\n{state['job_description']}"
        skill_improvements = get_gemini_response(improvement_prompt, context_data[0])

        # Get resume optimizations
        optimize_prompt = f"{PROMPTS['optimize']}\n\nJob Description:\n{state['job_description']}"
        resume_optimizations = get_gemini_response(optimize_prompt, context_data[0])

        # Update messages
        messages = state["messages"] + [
            timestamped_msg(content=f"[Agent3] ✅ ATS score generated: {ats_score[:100]}..."),
            timestamped_msg(content="[Agent3] ✅ Skill improvements suggested"),
            timestamped_msg(content="[Agent3] ✅ Resume optimizations provided")
        ]

        return {
            **state,
            "ats_score": ats_score,
            "skill_improvements": skill_improvements,
            "resume_optimizations": resume_optimizations,
            "messages": messages
        }

    except Exception as e:
        return {
            **state,
            "ats_score": "",
            "skill_improvements": "",
            "resume_optimizations": "",
            "messages": state["messages"] + [timestamped_msg(content=f"[Agent3] ❌ Error: {str(e)}")]
        }