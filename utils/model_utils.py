from langchain_groq import ChatGroq
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
def get_groq_llm(agent="agent1"):
    model = "Deepseek-R1-Distill-Llama-70b" if agent == "agent1" else "Llama3-70b-8192"
    key = st.session_state.get("groq_api_key", "")
    return ChatGroq(groq_api_key=key, model_name=model) if key else None


#for agent 3
#lets integrate and get the gemini llm
genai.configure(api_key=os.getenv("GEMINI_PRO_API_KEY"))


def get_gemini_response(prompt, context_data):
    """
    Function to interact with the Gemini-1.5-flash model.
    Takes a prompt and context data (resume/job description) and returns a generated response.
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Generate content using the provided prompt and context data
        response = model.generate_content([context_data, prompt])

        # Return the response text
        return response.text
    except Exception as e:
        return f"Error while generating content: {str(e)}"