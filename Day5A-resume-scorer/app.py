import streamlit as st
from google import genai
import json
import pandas as pd

st.set_page_config(page_title="Résumé Scorer", layout="wide")

st.title("Résumé vs JD Fit Scorer")
st.caption("Day 5 Lab 5A — Free tools end-to-end")

col1, col2 = st.columns(2)

with col1:
    resume = st.text_area("Paste résumé", height=400)

with col2:
    jd = st.text_area("Paste job description", height=400)

api_key = st.text_input(
    "Gemini API Key",
    type="password",
    help="Paste your Gemini API key from Google AI Studio"
)

if st.button("Score") and resume and jd and api_key:

    with st.spinner("Scoring..."):

        try:
            client = genai.Client(api_key=api_key)

            prompt = f"""
You are an expert placement coach.

Compare the following résumé and job description.

Return ONLY valid JSON in this exact format:

{{
    "score": 0,
    "technical_skills_match": 0,
    "soft_skills_match": 0,
    "experience_relevance": 0,
    "project_fit": 0,
    "rationale": "",
    "missing_skills": [],
    "suggestions": [],
    "learning_resources": [
        {{
            "skill": "",
            "resource_type": "",
            "link": ""
        }}
    ]
}}

Guidelines:
- All scores must be integers from 0-100.
- Suggest the top missing skills.
- Provide up to 3 free learning resources.
- Resource types can be YouTube, Course, Documentation, or Website.

Résumé:
{resume}

Job Description:
{jd}
"""

            resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            result = json.loads(resp.text)

            # Main Score
            st.metric("Fit Score", f"{result['score']}/100")

            # Feature A - Score Breakdown
            breakdown = pd.DataFrame(
                {
                    "Score": [
                        result.get("technical_skills_match", 0),
                        result.get("soft_skills_match", 0),
                        result.get("experience_relevance", 0),
                        result.get("project_fit", 0),
                    ]
                },
                index=[
                    "Technical Skills",
                    "Soft Skills",
                    "Experience",
                    "Project Fit",
                ],
            )

            st.subheader("Score Breakdown")
            st.bar_chart(breakdown)

            # Rationale
            st.subheader("Rationale")
            st.write(result.get("rationale", ""))

            # Missing Skills
            st.subheader("Missing Skills")
            for skill in result.get("missing_skills", []):
                st.write(f"- {skill}")

            # Suggestions
            st.subheader("Suggestions")
            for suggestion in result.get("suggestions", []):
                st.write(f"- {suggestion}")

            # Feature B - Learning Resources
            st.subheader("Top Missing Skills with Learning Resources")

            resources = result.get("learning_resources", [])

            if resources:
                for item in resources:
                    st.markdown(f"**Skill:** {item.get('skill', 'N/A')}")
                    st.markdown(f"**Resource Type:** {item.get('resource_type', 'N/A')}")
                    st.markdown(f"**Link:** {item.get('link', 'N/A')}")
                    st.write("---")
            else:
                st.info("No learning resources returned.")

        except Exception as e:
            st.error("Gemini service is currently busy or unavailable.")
            st.error(str(e))