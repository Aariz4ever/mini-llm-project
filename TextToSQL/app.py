from dotenv import load_dotenv
load_dotenv()  # Load all environment variables

import streamlit as st
import os
import sqlite3

import google.generativeai as genai

# Configure our API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load model and provide SQL query as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    full_prompt = f"{prompt}\n{question}"
    response = model.generate_content([full_prompt])
    return response.text

# Function to execute an SQL query
def execute_sql_query(sql, db):
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

# Defining your prompt
prompt = """
You are an expert in converting English questions to SQL query!
The SQL database has the name STUDENT and has the following columns - NAME, CLASS,
SECTION. For example,
Example 1 - How many entries of records are present?
The SQL command will be something like this: SELECT COUNT(*) FROM STUDENT;
Example 2 - Tell me all the students studying in Data Science class?
The SQL command will be something like this: SELECT * FROM STUDENT where CLASS="Data Science";
Example 3 - Update the marks of Aariz to 95
The SQL command will be something like this: UPDATE STUDENT SET MARKS = 95 WHERE NAME = "Aariz";
Example 4 - Delete the student with name Dhanush
The SQL command will be something like this: DELETE FROM STUDENT WHERE NAME = "Dhanush";
Also, the SQL code should not have ''' in beginning or end and sql word in output.
"""

# Streamlit App
st.set_page_config(page_title="I can retrieve any SQL query")
st.header("Gemini App to SQL")

question = st.text_input("Input: ", key="input")

submit = st.button("Ask Question")

# If submit is clicked
if submit:
    response = get_gemini_response(question, prompt)
    print(response)
    result = execute_sql_query(response, "student.db")
    st.subheader("The Response is")
    if isinstance(result, str):
        st.text(result)
    else:
        for row in result:
            print(row)
            st.text(row)
