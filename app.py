import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import fitz

st.title("Groq Bot")

# Inisialisasi GroqAI
load_dotenv()

key = os.getenv("GROQ_AI_API_KEY")
chat = ChatGroq(
    temperature=0,
    model="llama3-70b-8192",
    api_key=key
)

# Membuat template percakapan
system = "You are a helpful assistant."
human = "{text}"
groqPrompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

# Inisialisasi chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Menampilkan histori chat ketika ada prompt baru
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Fungsi untuk membaca PDF dan mengekstrak teks
def readPDF(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Upload PDF file
file = st.file_uploader("Upload PDF", type="pdf")
if file:
    fileContents = readPDF(file)

# React to user input
if grogInput := st.chat_input("Apa yang ingin Anda ketahui?"):
    # Menampilkan pesan/prompt dari user
    st.chat_message("user").markdown(grogInput)
    # Menambahkan pesan/prompt user ke dalam chat history
    st.session_state.messages.append({"role": "user", "content": grogInput})

    response = groqPrompt | chat

    try:
        if file:
            # Menggabungkan teks PDF dengan input user
            combinedInput = fileContents + "\n\n" + grogInput
            
            response = response.invoke({"text": combinedInput})
        else:
            response = response.invoke({"text": grogInput})   

        response = response.content
    except:
        response = "Maaf, permintaan anda tidak dapat dilakukan saat ini."

    # Menampilkan response dari groq atau pencarian
    with st.chat_message("assistant"):
        st.markdown(response)
    # Menambahkan response groq ke dalam chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
