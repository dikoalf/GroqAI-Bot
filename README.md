---

# Groq Bot Chatbot

Welcome to the Groq Bot Chatbot project! This is an advanced chatbot designed to provide intelligent, contextually aware responses. It leverages Groq AI's models for both conversational interaction, supports multiple languages, and allows PDF content integration for enhanced knowledge-based responses.

## Features

- **Automatic Language Detection**: The chatbot can detect and respond in the user's language, making interactions more seamless and user-friendly.
- **RAG-based Responses**: Uses Retrieval-Augmented Generation (RAG) to reference previously provided information and combine it with user queries for more accurate responses.
- **PDF Integration**: Upload PDFs to provide the bot with additional information. It processes, and uses the content to answer user queries.
- **Contextual Memory**: Retains chat history to maintain context across longer interactions, improving response relevance over time.
- **Text Chunking**: Efficiently chunks large texts, including PDFs.
- **Knowledge-based Interaction**: Dynamically builds a knowledge base using PDF contents and conversation history, enabling contextually aware responses based on past interactions.
- **Error Logging**: Captures errors with timestamps and saves them to Google Drive for easy troubleshooting.
- **Code Snippet Display**: Displays code snippets in a way that makes them easy to copy and use.

## Technology / Tools Used

- **Groq AI**: Groq AI models are used for chat (Llama 3 for chat).
- **Langchain**: A key framework to handle prompt templates and facilitate integration with language models.
- **Streamlit**: A fast and easy way to create a web interface for the chatbot.
- **Python**: Core programming language for developing the chatbot's logic and functionalities.
- **Google Drive API**: Used for saving chat history and error logs to Google Drive.
- **Deep Translator**: Facilitates language translation for multi-lingual support.

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
   Create a `.env` file in the root directory and add your Groq AI API key and Google Service Account info:
   ```plaintext
   GROQ_AI_API_KEY=your_api_key_for_chat_model
   GOOGLE_SERVICE_ACCOUNT_INFO='your_service_account_info_as_json_string'
   ```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and go to `http://localhost:8501` to interact with the chatbot.

## PDF Interaction

- Upload a PDF file to provide additional context to the chatbot.
- The chatbot will chunk the file, integrating this information into the conversation.

## Chat Interaction

- Enter your query into the chat input box.
- The bot will respond based on its knowledge, context memory, and any uploaded files.

## Error Logging

- Errors are captured along with timestamps and saved to Google Drive in `errorLog.json`.

## Code Snippet Display

- Code snippets are displayed in a format that makes them easy to copy and use.

## Code Overview

- `app.py`: Contains the main chatbot logic, including language detection, PDF upload, error logging, and conversation handling using Streamlit.
- `lib.py`: Utility file that handles PDF reading, text chunking, retrieval-augmented generation (RAG), and sliding window context management for memory. It also includes functions for Google Drive integration.
- `minsearch.py`: Provides the indexing and search functionality using MinSearch for efficient document retrieval and response generation based on cosine similarity and text vectorization.

## Example

Here's a brief example of how to use the chatbot:

1. Upload a PDF file for additional context.
2. Ask the chatbot any question related to the document or a general query.
3. The bot will utilize its knowledge base, memory, and context-aware features to generate a relevant response.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---