import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import fitz
import langid
import minsearch

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
system = """Kamu adalah asisten. 
Selalu menjawab pertanyaan mengunakan bahasa {language}.
"""
human = "{text}"
groqPrompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

# Inisialisasi Index
index = minsearch.Index(text_fields=["input","content"], keyword_fields=[])

# Inisialisasi knowledgeBased
if "knowledgeBased" not in st.session_state:
    st.session_state.knowledgeBased = []

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

    # untuk menghasilkan response dari model sesuai dengan template chat
    response = groqPrompt | chat

    try:
        if file:
            # Tambahkan konten file ke dalam Index
            st.session_state.knowledgeBased.append({"input":"File","content": fileContents})
        
        language, confidence = langid.classify(grogInput)
        searchResult = {}

        if st.session_state.knowledgeBased:

            index.fit(st.session_state.knowledgeBased)
            
            # Cari di Index menggunakan MinSearch
            searchResult = index.search(
                query = grogInput, 
                boost_dict= {'content': 3.0, 'input': 0.5},
                num_results=min(len(st.session_state.knowledgeBased), 5)
            )

        if searchResult:
            combinedInput = "\n\n".join([result["content"] for result in searchResult]) + "\n\n" + grogInput
        else:
            combinedInput = grogInput
        
        response = response.invoke({"text": combinedInput, "language": language})
        response = response.content

        # Tambahkan input dan response ke dalam Index
        st.session_state.knowledgeBased.append({"input":grogInput,"content": response})
    except Exception as e:
        response = f"Maaf, permintaan anda tidak dapat dilakukan saat ini. Error: {e}"

    # Menampilkan response dari groq atau pencarian
    with st.chat_message("assistant"):
        st.markdown(response)
    # Menambahkan response groq ke dalam chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
