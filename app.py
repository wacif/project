# -*- coding: utf-8 -*-
# Streamlit-based UI for the scraper and OpenAI processing

import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Function to validate the link
def is_valid_link(link: str) -> bool:
    """Validate if the provided link is a valid HTML link."""
    try:
        response = requests.get(link, timeout=5)
        return response.status_code == 200 and 'text/html' in response.headers['Content-Type']
    except Exception:
        return False

# Function to scrape HTML
def scrape_html(link: str) -> str:
    """Scrape content from the HTML link."""
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

# Streamlit UI implementation
st.title("HTML Data Extractor and OpenAI Processor")

# Input fields
link = st.text_input("Enter the URL to scrape:")
api_key = st.secrets["API"]

# Template for JSON output
template = """'''
{
    "data": [
        {
            "Highest_Qualification_Held": "",
            "Experience_in_Years": 0,
            "Current_Job_Title": "",
            "Current_Employer": "",
            "Skill_Set": "",
            "Experience_Details": [
                {
                    "Company": "",
                    "I_currently_work_here": false,
                    "Summary": "",
                    "Work_Duration": {
                        "from": "",
                        "to": ""
                    },
                    "Occupation_Title": ""
                }
            ],
            "Educational_Details": [
                {
                    "Institute_School": "",
                    "Currently_pursuing": false,
                    "Degree": "",
                    "Duration": {
                        "from": "",
                        "to": ""
                    }
                }
            ]
        }
    ]
}
'''"""

# Prompts
SYSTEM_PROMPT = """You are a smart assistant that extracts the requested information accurately."""

USER_PROMPT_TEMPLATE = """
Process the raw data below and extract the following details:
1. General Info:
   - Highest Qualification Held
   - Experience in Years
   - Current Job Title
   - Current Employer
   - Skill Set
2. Experience Details:
   - Company
   - Currently working there (True/False)
   - Summary
   - Work Duration (from/to)
   - Occupation Title
3. Educational Details:
   - Institute/School
   - Currently pursuing (True/False)
   - Degree
   - Duration (from/to)

Format the output as a JSON object matching this template:
{template}

Notes:
1. Use NILL for missing values. If "from" or "to" dates are missing, use the current date.
2. If multiple entries exist, append each separately.
3. Strictly follow the given instructions and JSON format.

Raw Data:
{data}
"""


# Process button
if st.button("Process"):
    if not is_valid_link(link):
        st.error("Invalid URL. Please check and try again.")
    else:
        with st.spinner("Scraping HTML data..."):
            raw_data = scrape_html(link)

        # Build the user prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(data=raw_data, template=template)

        with st.spinner("Processing data with OpenAI..."):
            try:
                # OpenAI API call
                openai.api_key = api_key
                completion = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ]
                )
                response = completion.choices[0].message.content
                prompt_tokens = completion.usage.prompt_tokens
                output_tokens = completion.usage.completion_tokens
                total_tokens = completion.usage.total_tokens
                st.json(response)  # Display JSON response
                st.write(f"Input Tokens: {prompt_tokens}")
                st.write(f"Output Tokens: {output_tokens}")
                st.write(f"Total Tokens: {total_tokens}")
            except Exception as e:
                st.error(f"Error during OpenAI processing: {e}")
