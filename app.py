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

# Prompts for OpenAI
SYSTEM_PROMPT = """You are a smart assistant that reads the provided data smartly and extracts the mentioned key values. Strictly follow the user's instructions."""
USER_PROMPT_TEMPLATE = """
Here is the raw data to process and extract key values smartly:
{data}
Now your task is:
1- extract the following information from the data:
Highest_Qualification_Held, Experience_in_Years, Current_Job_Title, Current_Employer, Skill_Set.
2- extract the experience and its details like:
company, currently work at that company or not, summary of that experience, work duration, period (from & to), and then occupation title.
3- extract educational details like:
institute or school, currently pursuing or not, degree name, and duration (from & to).
After the data extraction, structure the data like the JSON template below.
{template}

Note:
1- Use NILL for missing values. If "from" or "to" dates are missing, use the current date.
2- If you found two or more sets of any value, append them accordingly.

Output **only** a valid JSON object. Do not include any extra text, comments, or explanations from your side.
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
                st.json(response)  # Display JSON response
            except Exception as e:
                st.error(f"Error during OpenAI processing: {e}")
