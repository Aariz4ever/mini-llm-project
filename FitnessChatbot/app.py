from dotenv import load_dotenv
load_dotenv()  # Load all environment variables

import streamlit as st
import os
import sqlite3
import google.generativeai as genai
from datetime import datetime, timedelta
import re

# Configure our API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load model and provide SQL query as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    return response.text.strip().replace("'", "''")  # Escape single quotes for SQL queries

# Function to execute an SQL query
def execute_sql_query(sql, db):
    print("Executing SQL query:", sql)  # Debug output
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        if sql.strip().lower().startswith('select'):
            cur.execute(sql)
            rows = cur.fetchall()
            result = rows
        else:
            cur.execute(sql)
            conn.commit()
            result = f"Query executed successfully: {sql}"
    except sqlite3.Error as e:
        result = f"An error occurred: {e}"
    conn.close()
    return result

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
    recommendations = "Give me a diet recommendation for breakfast, lunch, dinner for my health conditions mentioned below:\n"

    if glucose:
        recommendations += f"- Glucose Level: {glucose[1]}\n"

    if steps:
        recommendations += f"- Step Count: {steps[1]}\n"

    if calories:
        recommendations += f"- Calorie Intake: {calories[1]}\n"

    if not glucose and not steps and not calories:
        recommendations += "- No recent health data available. Please log your activities for personalized recommendations."

    return recommendations

# Helper function to replace relative dates with absolute dates
def replace_relative_dates(question):
    today = datetime.today().date()
    yesterday = today - timedelta(days=1)
    
    question = question.replace("today", str(today))
    question = question.replace("yesterday", str(yesterday))
    
    return question

# Helper function to handle user input for saving data
def handle_user_input(question, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    patterns = {
        "calorie intake": re.compile(r"i consumed (\d+) calories today", re.IGNORECASE)
    }

    for key, pattern in patterns.items():
        match = pattern.search(question)
        if match:
            value = int(match.group(1))
            if key == "calorie intake":
                cur.execute("INSERT OR REPLACE INTO CalorieTracking (Date, Calories) VALUES (?, ?)", (now, value))
            conn.commit()
            conn.close()
            return f"Recorded your {key} as {value} for today."
    
    conn.close()
    return "No relevant data to record."

# Streamlit App
st.set_page_config(page_title="Fitness App Chatbot")
st.header("Fitness App Chatbot")

prompt = """
You are an expert in converting English questions to SQL query!
The SQL database has the following tables and columns:
1. GlucoseLevel (Date, Level)
2. StepCount (Date, Steps)
3. HeartRate (Date, Rate)
4. CalorieTracking (Date, Calories)

Examples:
1. What was my glucose level on 2023-05-21?
   SQL: SELECT Level FROM GlucoseLevel WHERE Date='2023-05-21';
2. Update my step count on 2023-05-21 to 10000.
   SQL: UPDATE StepCount SET Steps=10000 WHERE Date='2023-05-21';
3. Delete my heart rate record for 2023-05-21.
   SQL: DELETE FROM HeartRate WHERE Date='2023-05-21';
4. How many calories did I consume on 2023-05-21?
   SQL: SELECT Calories FROM CalorieTracking WHERE Date='2023-05-21';
5. I consumed 2500 calories today.
   SQL: INSERT OR REPLACE INTO CalorieTracking (Date, Calories) VALUES ('2023-05-21', 2500);

When the user asks for diet recommendations or workout plans, generate personalized suggestions based on their data.
Also, the SQL code should not have ''' in beginning or end and sql word in output.
"""

question = st.text_input("Input your question: ", key="input")

submit = st.button("Ask Question")

# If submit is clicked
if submit:
    # Replace relative dates with absolute dates
    question = replace_relative_dates(question)

    # Check if the question contains data to be saved
    save_response = handle_user_input(question, "fitness.db")
    if "Recorded your" in save_response:
        st.subheader("The Response is")
        st.text(save_response)
    else:
        if "diet recommendation" in question.lower() or "workout plan" in question.lower():
            prompt = generate_recommendations()
            response = get_gemini_response(question, prompt)
            if response.startswith("An error occurred"):
                st.subheader("Error")
                st.text(response)
            else:
                result = execute_sql_query(response, "fitness.db")
                st.subheader("The Response is")
                if isinstance(result, str):
                    st.text(result)
                else:
                    for row in result:
                        st.text(row)
        else:
            response = get_gemini_response(question, prompt)
            if response.startswith("An error occurred"):
                st.subheader("Error")
                st.text(response)
            else:
                result = execute_sql_query(response, "fitness.db")
                st.subheader("The Response is")
                if isinstance(result, str):
                    st.text(result)
                else:
                    for row in result:
                        st.text(row)
