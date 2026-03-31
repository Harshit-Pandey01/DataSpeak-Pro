import os
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Initialize the GenAI Client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(question, prompt):
    """Generates SQL query using Gemini"""
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=[f"{prompt}\n\nQuestion: {question}"],
        config=types.GenerateContentConfig(
            temperature=0.1,
        )
    )
    return response.text.strip().replace("```sql", "").replace("```", "")

def read_sql_query(sql, db):
    """Executes SQL and returns results"""
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [description[0] for description in cur.description]
        conn.close()
        return rows, columns
    except Exception as e:
        return str(e), None

# --- MODERN STREAMLIT UI ---
st.set_page_config(page_title="SQL Genius AI", page_icon="🤖", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stTextInput > div > div > input { background-color: #262730; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 SQL Genius: Text-to-Data")
st.markdown("Convert natural language into SQL queries and fetch results instantly.")

# Define the Expert Prompt
PROMPT = """
You are an expert in converting English questions to SQL queries!
The database is named STUDENT with columns: NAME, CLASS, SECTION, MARKS.
Rules:
1. Only return the SQL query.
2. Do not include markdown code blocks (```).
3. Do not include the word 'sql' in the output.
Example: 'How many records?' -> SELECT COUNT(*) FROM STUDENT;
"""

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history (including tables)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        # If the message contains query data, display the table again
        if "query_data" in message:
            st.table(message["query_data"])

# Chat Input
if question := st.chat_input("Ask your database (e.g., 'Show me all students in AI class')"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.status("Generating SQL Query...", expanded=False) as status:
            generated_sql = get_gemini_response(question, PROMPT)
            st.code(generated_sql, language="sql")
            status.update(label="Query Generated!", state="complete")

        # Execute Query
        data, cols = read_sql_query(generated_sql, "student.db")

        if cols and isinstance(data, list):
            # Format data into a list of dictionaries for st.table
            table_results = [dict(zip(cols, row)) for row in data]
            
            if len(table_results) > 0:
                st.success("Query Results:")
                st.table(table_results)
                
                # Add to session state with the table data
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Found {len(data)} results for: `{generated_sql}`",
                    "query_data": table_results # Save the table data here
                })
            else:
                st.warning("No records found for that query.")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"No records found for: `{generated_sql}`"
                })
        else:
            st.error(f"Error: {data}")






