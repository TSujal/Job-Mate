# 🤖 JobMate: Your AI-Powered Job Application Assistant

**JobMate** is a **multi-agent AI system** designed to simplify and supercharge the job application process — especially for students and job seekers. It simulates a team of smart agents that assist in every step of the job hunting process — from scraping jobs to tailoring resumes and cover letters with human-like intelligence.

---

## 🚀 Features

### 🕷 Agent 1: Job Description Scraper
- Scrapes job listings (currently from **LinkedIn**, future support for **Indeed**, **Glassdoor**, etc.)
- Extracts full job description for a chosen listing
- Built-in roadmap for scraping via **MCP servers**

### 📄 Agent 2: Cover Letter Generator
- Takes user's resume, past cover letter, LinkedIn, portfolio links
- Tailors a **new cover letter** customized for each job
- Uses LLM-based decision making to simulate a professional writing assistant

### 🧠 Agent 3: Resume Tailor & ATS Analyzer
- Analyzes resume vs. job description
- Calculates **ATS (Applicant Tracking System) Score**
- Gives concrete feedback like:
  - High/Medium/Low impact suggestions
  - Which keywords/skills to improve
  - How to make your resume job-specific

---

## 🔁 Multi-Agent Architecture

- All agents **communicate with each other** using **LangGraph**
- Simulates realistic human-agent collaboration
- Human intervention/feedback box allows further tweaking of generated outputs
- Uses a **modular, scalable design** — each agent is replaceable/extendable

---

## 🎯 Future Goals

- 🔌 Integration with **MCP servers** to scale job scraping & management
- 🤝 Add 4-5 more intelligent agents for:
  - Job ranking
  - Auto-submission of applications
  - Skill gap analysis
  - Tracking applied jobs
- 🧠 Continuously improving agents using user data (RAG & RLHF pipelines)

---

## 🧱 Tech Stack

| Area                  | Stack                            |
|-----------------------|----------------------------------|
| Backend & Agents      | Python, LangGraph, LLMs          |
| Web Interface         | Streamlit                        |
| Scraping              | PlayWright (for LinkedIn)        |
| Data & Orchestration  | JSON, API integrations           |
| Deployment (WIP)      | GitHub, MCP (future)             |

---

## 🤝 Contributing

Pull requests are welcome. Please open an issue first to discuss what you would like to change or add.

---

## 📫 Contact

Built by **Sujal Thakkar**  
📧 thakkar.su@northeastern.edu  
🔗 [LinkedIn](https://www.linkedin.com/in/sujal-thakkar/) • [GitHub](https://github.com/TSujal)

---
