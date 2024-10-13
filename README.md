---

# Groq Bot Chatbot

Welcome to the Groq Bot Chatbot project! This is an advanced chatbot designed to provide intelligent, contextually aware responses. It leverages Groq AI's models for both conversational interaction and summarization, supports multiple languages, and allows PDF content integration for enhanced knowledge-based responses.

## Features

- **Automatic Language Detection**: The chatbot can detect and respond in the user's language, making interactions more seamless and user-friendly.
- **Enhanced Contextual Understanding**: By integrating a retrieval-augmented generation (RAG) approach, the chatbot can reference previous topics and provide more coherent and contextually relevant responses.
- **PDF Integration**: Users can upload PDF files, and the bot can extract, summarize, and use the content to answer questions.
- **Contextual Memory**: Retains conversation history, improving the flow of longer interactions by maintaining relevant context.
- **Text Vectorization & Cosine Similarity**: Uses TF-IDF for vectorizing text, enabling more accurate search results and improving chatbot intelligence.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dikoalf/GroqAI-Bot.git
   cd GroqAI-Bot
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add your Groq AI API key:
   ```plaintext
   GROQ_AI_API_KEY=your_api_key_for_chat_model
   GROQ_AI_API_KEY2=your_api_key_for_summary_model
   ```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and go to `http://localhost:8501` to interact with the chatbot.

## Code Overview

- `app.py`: Main file containing the Streamlit interface and chatbot logic, including PDF upload and conversation management.
- `lib.py`: Utility functions for PDF extraction, text chunking, RAG implementation, and sliding window memory management.

## Example

Here's a brief example of how to use the chatbot:

1. Upload a PDF file to provide additional context for the chatbot.
2. Enter your query in the chat input box.
3. The chatbot will respond with contextually relevant information, referencing the uploaded PDF if applicable.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---
