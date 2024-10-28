import sqlite3
import os
import openai
import faiss
import numpy as np
import time
from openai.error import RateLimitError

# Database file
DB_FILE = 'knowledge_base.db'

# Create database connection
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables in SQLite
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transcripts (
        video_id TEXT PRIMARY KEY,
        title TEXT,
        transcript TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS embeddings (
        video_id TEXT PRIMARY KEY,
        embedding BLOB
    )
''')
conn.commit()

# FAISS index for embeddings
dimension = 1536  # Dimension of OpenAI embeddings
index = faiss.IndexFlatL2(dimension)

def insert_transcript(video_id, title, transcript):
    """Insert transcript data into the database."""
    cursor.execute(
        "INSERT OR REPLACE INTO transcripts (video_id, title, transcript) VALUES (?, ?, ?)",
        (video_id, title, transcript)
    )
    conn.commit()

def create_embedding(text):
    """Generate an embedding for the given text using OpenAI API, with error handling."""
    while True:
        try:
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=[text]
            )
            embedding = np.array(response['data'][0]['embedding'], dtype=np.float32)
            return embedding
        except RateLimitError:
            print("Rate limit exceeded, waiting 10 seconds before retrying...")
            time.sleep(10)  # Wait 10 seconds before retrying

def insert_embedding(video_id, embedding):
    """Insert the embedding data into the database and FAISS index."""
    # Convert embedding to binary for SQLite storage
    embedding_blob = embedding.tobytes()
    cursor.execute(
        "INSERT OR REPLACE INTO embeddings (video_id, embedding) VALUES (?, ?)",
        (video_id, embedding_blob)
    )
    index.add(np.array([embedding]))  # Add to FAISS index
    conn.commit()

def load_transcripts_and_create_embeddings():
    """Load each transcript, create its embedding, and populate the knowledge base."""
    for filename in os.listdir("transcripts"):
        if filename.endswith(".txt"):
            video_id = filename.split(".")[0]
            with open(os.path.join("transcripts", filename), "r") as f:
                transcript = f.read()
                # For simplicity, use video_id as title
                title = f"Transcript {video_id}"
                insert_transcript(video_id, title, transcript)
                embedding = create_embedding(transcript)
                insert_embedding(video_id, embedding)
                print(f"Inserted transcript and embedding for {video_id}")
                time.sleep(1)  # Pause for 1 second between API calls

if __name__ == "__main__":
    load_transcripts_and_create_embeddings()
    print("Knowledge base populated.")

