import os
import streamlit as st
import csv
import time
import pandas as pd
from scripts.rag_flow import rag_query

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OpenAI API key is missing! Please set it as an environment variable.")

# Initialize CSV logging
LOG_FILE = 'query_logs.csv'

# Ensure log file exists with headers
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "query", "response", "response_time", "feedback"])

# Streamlit app configuration
st.title("Mind The Game - Podcast Q&A")
st.write("Ask any question about the Mind The Game podcast, and get insights based on relevant episodes!")

# Input query
user_query = st.text_input("Enter your question here:")

# Query the RAG pipeline and display the answer
if st.button("Get Answer"):
    if user_query:
        start_time = time.time()
        with st.spinner("Generating response..."):
            answer = rag_query(user_query)
            response_time = time.time() - start_time
            st.write("**Answer:**", answer)

            # Log the query and response
            with open(LOG_FILE, mode='a') as file:
                writer = csv.writer(file)
                writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), user_query, answer, round(response_time, 2), ""])

            # Add feedback options
            feedback = st.radio("Was this answer helpful?", ("👍 Yes", "👎 No"))
            if feedback:
                with open(LOG_FILE, mode='a') as file:
                    writer = csv.writer(file)
                    writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), user_query, answer, round(response_time, 2), feedback])

    else:
        st.write("Please enter a question to get started.")

# Display monitoring metrics
if st.sidebar.checkbox("Show Monitoring Dashboard"):
    st.sidebar.subheader("Query Monitoring")
    df = pd.read_csv(LOG_FILE)

    # Display basic stats
    st.sidebar.write("**Total Queries:**", len(df))
    st.sidebar.write("**Average Response Time (s):**", round(df['response_time'].mean(), 2))

    # Feedback summary
    feedback_counts = df['feedback'].value_counts()
    st.sidebar.write("**Feedback Summary:**")
    st.sidebar.bar_chart(feedback_counts)

    # Additional charts
    st.sidebar.subheader("Queries Over Time")
    st.sidebar.line_chart(df.groupby('timestamp').size())

    st.sidebar.subheader("Response Time Distribution")
    st.sidebar.hist_chart(df['response_time'])

