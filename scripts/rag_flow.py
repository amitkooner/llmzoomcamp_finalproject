import os
import sqlite3
import openai
import faiss
import numpy as np
import time
from openai.error import RateLimitError

# Retrieve OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OpenAI API key is missing! Please set it as an environment variable.")

# Database and FAISS setup
DB_FILE = 'knowledge_base.db'
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

dimension = 1536  # Dimension of OpenAI embeddings
index = faiss.IndexFlatL2(dimension)

# Load embeddings from the database into FAISS
def load_embeddings():
    cursor.execute("SELECT video_id, embedding FROM embeddings")
    embeddings = []
    video_ids = []
    for row in cursor.fetchall():
        video_id, embedding_blob = row
        embedding = np.frombuffer(embedding_blob, dtype=np.float32)
        embeddings.append(embedding)
        video_ids.append(video_id)
    index.add(np.array(embeddings))
    return video_ids

# Load the embeddings into memory
video_ids = load_embeddings()

def create_query_embedding(query):
    """Generate an embedding for the user query."""
    while True:
        try:
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=[query]
            )
            query_embedding = np.array(response['data'][0]['embedding'], dtype=np.float32)
            return query_embedding
        except RateLimitError:
            print("Rate limit exceeded, waiting 10 seconds before retrying...")
            time.sleep(10)

def preprocess_query(query):
    """Preprocess the query by removing stop words and normalizing case."""
    stop_words = {"a", "the", "is", "are", "and", "or"}
    return " ".join(word.lower() for word in query.split() if word.lower() not in stop_words)

def hybrid_search(query, top_k=3):
    """Combine exact text search and FAISS vector search for hybrid retrieval."""
    # Text search for exact matches
    text_matches = []
    cursor.execute("SELECT video_id, transcript FROM transcripts WHERE transcript LIKE ?", (f"%{query}%",))
    for row in cursor.fetchall():
        video_id, transcript = row
        text_matches.append((video_id, transcript))

    # Vector search with FAISS
    query_embedding = create_query_embedding(query)
    _, indices = index.search(np.array([query_embedding]), top_k)
    vector_matches = [video_ids[i] for i in indices[0]]

    # Combine and re-rank results
    combined_results = text_matches + [(vid, None) for vid in vector_matches if vid not in [vm[0] for vm in text_matches]]
    return combined_results[:top_k]

def re_rank_results(query, transcripts):
    """Re-rank transcripts based on keyword overlap with the query."""
    query_keywords = set(query.lower().split())
    ranked_transcripts = sorted(
        transcripts,
        key=lambda t: len(query_keywords.intersection(t.lower().split())),
        reverse=True
    )
    return ranked_transcripts

def retrieve_relevant_transcripts(query, top_k=3):
    """Retrieve the most relevant transcripts using hybrid search and re-rank them."""
    results = hybrid_search(query, top_k)
    transcripts = []
    for video_id, transcript in results:
        if transcript is None:  # Retrieve transcript for vector-only matches
            cursor.execute("SELECT transcript FROM transcripts WHERE video_id = ?", (video_id,))
            transcript = cursor.fetchone()[0]
        transcripts.append(transcript)
    return re_rank_results(query, transcripts)

def generate_response(query, transcripts):
    """Generate a response using OpenAI's language model, based on retrieved transcripts."""
    prompt = f"Answer the following query based on the information below.\n\nQuery: {query}\n\nRelevant information:\n"
    for i, transcript in enumerate(transcripts, 1):
        prompt += f"\nTranscript {i}: {transcript}\n"
    prompt += "\n\nAnswer:"

    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            return response['choices'][0]['message']['content'].strip()
        except RateLimitError:
            print("Rate limit exceeded, waiting 10 seconds before retrying...")
            time.sleep(10)

def rag_query(query):
    """Main RAG function to handle a user query."""
    query = preprocess_query(query)  # Preprocess query
    transcripts = retrieve_relevant_transcripts(query)
    response = generate_response(query, transcripts)
    return response

if __name__ == "__main__":
    user_query = input("Enter your query: ")
    answer = rag_query(user_query)
    print("Answer:", answer)
