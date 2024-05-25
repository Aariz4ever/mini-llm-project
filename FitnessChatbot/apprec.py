from dotenv import load_dotenv
import os
import sqlite3
import google.generativeai as genai
from datetime import datetime
import re
import streamlit as st
import webbrowser

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Generative Model
model = genai.GenerativeModel("gemini-pro")

# Function to get response from Generative AI
def get_gemini_response(question):
    response = model.generate_content(question)
    return response.text

# Function to fetch data from SQLite database
def fetch_sql_data(table_name):
    connection = sqlite3.connect('fitness.db')
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY Date DESC LIMIT 1")
    data = cursor.fetchone()
    connection.close()
    return data

# Function to generate personalized diet and workout recommendations
def generate_recommendations():
    # Connect to the database
    conn = sqlite3.connect('fitness.db')
    cur = conn.cursor()

    # Fetch the latest data
    cur.execute("SELECT * FROM GlucoseLevel ORDER BY Date DESC LIMIT 1")
    glucose = cur.fetchone()

    cur.execute("SELECT * FROM StepCount ORDER BY Date DESC LIMIT 1")
    steps = cur.fetchone()

    cur.execute("SELECT * FROM CalorieTracking ORDER BY Date DESC LIMIT 1")
    calories = cur.fetchone()

    conn.close()

    # Generate recommendations based on the fetched data
    recommendations = """Can you provide a list of [number] breakfast, lunch, and dinner food ideas that are [specific dietary restriction or preference, e.g. vegetarian, gluten-free, low-carb, etc.]? Please include a variety of options and provide a brief description of each dish. You can use [specific ingredients or cuisines, e.g. Mediterranean, Asian-inspired, etc.] as inspiration. Additionally, please ensure that the list includes a mix of [specific nutritional requirements, e.g. high-protein, low-fat, etc.]. for my health conditions mentioned below in provided example :\n"""

    if glucose:
        recommendations += f"- Glucose Level: {glucose[1]}\n"

    if steps:
        recommendations += f"- Step Count: {steps[1]}\n"

    if calories:
        recommendations += f"- Calorie Intake: {calories[1]}\n"

    if not glucose and not steps and not calories:
        recommendations += "- No recent health data available. Please log your activities for personalized recommendations."

    return recommendations

# Function to handle user input
def handle_user_input(question, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    patterns = {
        "calorie intake": re.compile(r"i consumed (\d+) calories today", re.IGNORECASE),
        "open youtube": re.compile(r"open youtube", re.IGNORECASE)
    }

    for key, pattern in patterns.items():
        match = pattern.search(question)
        if match:
            if key == "calorie intake":
                value = int(match.group(1))
                cur.execute("INSERT OR REPLACE INTO CalorieTracking (Date, Calories) VALUES (?, ?)", (now, value))
                conn.commit()
                conn.close()
                return f"Recorded your {key} as {value} for today."
            elif key == "open youtube":
                webbrowser.open("https://www.youtube.com/")
                return "Opening YouTube..."
    
    conn.close()
    return "No relevant data to record."


# Initialize Streamlit app
st.set_page_config(page_title="Q&A Demo")
st.header("Gemini LLM Application")

# User input
input_text = st.text_input("Input: ", key="input")
submit_button = st.button("Ask the question")

# When submit button is clicked
if submit_button:
    # Print the prompt to the console
    print("Prompt to be executed:", generate_recommendations())
    
    # Get response from Generative AI
    response = get_gemini_response(input_text)
    st.subheader("The Response is")
    st.write(response)