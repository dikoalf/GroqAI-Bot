---

# Groq Bot Chatbot

Welcome to the Groq Bot Chatbot project! This chatbot is designed to provide intelligent and contextually relevant responses to user queries. It supports automatic language detection, enhanced contextual understanding, and PDF integration.

## Features

- **Automatic Language Detection**: The chatbot can detect and respond in the user's language, making interactions more seamless and user-friendly.
- **Enhanced Contextual Understanding**: By integrating a retrieval-augmented generation (RAG) approach, the chatbot can reference previous topics and provide more coherent and contextually relevant responses.
- **PDF Integration**: Users can upload PDF files, and the chatbot can extract and utilize the content to provide more informed answers.
- **Dynamic Search Results**: The chatbot dynamically adjusts the number of search results based on the content available, ensuring the most relevant information is always provided.
- **Text Vectorization**: The chatbot utilizes text vectorization techniques to better understand and process natural language input, enhancing the quality of responses.
- **Memory**: The chatbot incorporates memory capabilities to retain context and information across interactions, leading to more personalized and accurate conversations.

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
   GROQ_AI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and go to `http://localhost:8501` to interact with the chatbot.

## Code Overview

- `app.py`: Main application file that sets up the Streamlit interface and integrates the chatbot functionalities.
- `minsearch.py`: Contains the search functionality using `pandas`, `scikit-learn`, and `numpy`.

## Example

Here's a brief example of how to use the chatbot:

1. Upload a PDF file to provide additional context for the chatbot.
2. Enter your query in the chat input box.
3. The chatbot will respond with contextually relevant information, referencing the uploaded PDF if applicable.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---
