# Mind The Game - Podcast Q&A

This project creates a Retrieval-Augmented Generation (RAG) flow for a Q&A application based on transcripts from the *Mind The Game* podcast, a popular basketball podcast featuring NBA legend **LeBron James** and his former teammate-turned-coach, **JJ Redick**. In this unique show, the two discuss the ins and outs of basketball, often over a glass of wine, sharing insights into the game, leadership, and their personal journeys.

LeBron, known as one of the greatest basketball players of all time, now plays under JJ Redick’s coaching on the Los Angeles Lakers. Their candid conversations provide an in-depth look at the NBA world from the perspective of a player and a coach, making it a treasure trove for fans who want to learn more about basketball strategies, player dynamics, and the culture surrounding the sport.

This project enables users to interact with *Mind The Game* content by asking questions and receiving answers based on relevant episodes, allowing fans to engage deeply with LeBron and JJ's discussions.

---

## Project Overview

This Q&A system is built with the following key components:
- **Knowledge Base**: Stores podcast transcripts in both text and vector formats, enabling fast and relevant retrieval.
- **LLM Integration**: Uses OpenAI’s `gpt-3.5-turbo` model to generate responses based on relevant transcripts.
- **Hybrid Retrieval**: Combines exact text search and vector similarity search to retrieve the most relevant content.
- **Enhanced Monitoring**: Tracks and visualizes user feedback and query metrics with Streamlit for real-time performance insights.

## Prerequisites

- **OpenAI API Key**: Required for querying OpenAI's language model.
  - Obtain an API key from [OpenAI](https://platform.openai.com/account/api-keys) and keep it ready for configuration.
- **Docker**: Ensure that Docker and Docker Compose are installed on your system.

## Setup Instructions

### Environment Variables

This project uses environment variables to securely configure the OpenAI API key. Make sure to set up the following variable in the Docker Compose file.

1. **OpenAI API Key**: In the `docker-compose.yml` file, replace `your_openai_api_key_here` with your actual OpenAI API key:

    ```yaml
    environment:
      - OPENAI_API_KEY=your_openai_api_key_here
    ```

### Installation and Running the Application

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/MIND_THE_GAME_RAG_PROJECT.git
   cd MIND_THE_GAME_RAG_PROJECT

2. ***Build and Run the Docker Container***

Build the Docker container and start the application using Docker Compose:

```bash
docker-compose up --build
```

This command will install dependencies, set up the environment, and start the Streamlit app.

3. ***Using the App***

Ask Questions: Enter a question in the text box to receive answers based on relevant podcast episodes.
Provide Feedback: After receiving an answer, rate it with a thumbs-up or thumbs-down.
Monitoring Dashboard: Use the sidebar to open the monitoring dashboard, displaying feedback metrics, query volume, and response times.

---

This README now includes all necessary setup and installation details, as well as instructions for configuring the environment variables. Let me know if there’s anything else you’d like to add or clarify!
