---

Groq Bot Chatbot

Welcome to the Groq Bot Chatbot project! This is an advanced chatbot designed to provide intelligent, contextually aware responses. It leverages Groq AI's models for both conversational interaction and summarization, supports multiple languages, and allows PDF content integration for enhanced knowledge-based responses.
Features

    Automatic Language Detection: Detects the user's language and responds accordingly, making interactions smoother.
    Retrieval-Augmented Generation (RAG): Enhances chatbot responses by referencing relevant information from previously uploaded content or conversation history.
    PDF Content Integration: Users can upload PDF files, and the bot can extract, summarize, and use the content to answer questions.
    Contextual Memory: Retains conversation history, improving the flow of longer interactions by maintaining relevant context.
    Text Vectorization & Cosine Similarity: Uses TF-IDF for vectorizing text, enabling more accurate search results and improving chatbot intelligence.

Installation

    Clone the repository:

    bash

git clone https://github.com/dikoalf/GroqAI-Bot.git
cd GroqAI-Bot

Set up a virtual environment and activate it:

bash

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Install the required dependencies:

bash

pip install -r requirements.txt

Set up environment variables: Create a .env file in the root directory and add your Groq AI API keys:

plaintext

    GROQ_AI_API_KEY=your_api_key_for_chat_model
    GROQ_AI_API_KEY2=your_api_key_for_summary_model

Usage

    Run the Streamlit app:

    bash

    streamlit run app.py

    Open your browser and go to http://localhost:8501 to interact with the chatbot.

Code Overview

    app.py: Main file containing the Streamlit interface and chatbot logic, including PDF upload and conversation management.
    lib.py: Utility functions for PDF extraction, text chunking, RAG implementation, and sliding window memory management.

Example Usage

    Upload a PDF file to provide the bot with additional knowledge.
    Enter your query in the chatbox.
    The chatbot will respond with contextually relevant information, potentially incorporating content from the uploaded PDF.

Contributing

Contributions are welcome! Please fork the repository and create a pull request with your proposed changes.

---
