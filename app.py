import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import fitz
import langid
import minsearch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

# Inisialisasi memory
if "memory" not in st.session_state:
    st.session_state.memory = []

# Inisialisasi TfidfVectorizer
vectorizer = TfidfVectorizer()

# Fungsi untuk membaca PDF dan mengekstrak teks
def readPDF(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Fungsi untuk vectorize texts
def vectorize_texts(texts):
    return vectorizer.fit_transform(texts)

# Upload PDF file
file = st.file_uploader("Upload PDF", type="pdf")
if file:
    fileContents = readPDF(file)

# Menampilkan histori chat ketika ada prompt baru
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if grogInput := st.chat_input("Apa yang ingin Anda ketahui?"):
    # Menampilkan pesan/prompt dari user
    st.chat_message("user").markdown(grogInput)
    # Menambahkan pesan/prompt user ke dalam chat history
    st.session_state.messages.append({"role": "user", "content": grogInput})
    
    # Menambahkan percakapan baru ke memori
    st.session_state.memory.append({
        "role": "user",
        "content": grogInput
    })

    # untuk menghasilkan response dari model sesuai dengan template chat
    response = groqPrompt | chat

    try:
        if file:
            # Tambahkan konten file ke dalam Index dan knowledgeBased
            st.session_state.knowledgeBased.append({"input":"File","content": fileContents})

        # Lakukan vektorisasi knowledgeBase content
        if st.session_state.knowledgeBased:
            knowledge_texts = [item["content"] for item in st.session_state.knowledgeBased]
            vectorized_knowledge = vectorize_texts(knowledge_texts)
        
        language, confidence = langid.classify(grogInput)
        searchResult = {}

        if st.session_state.knowledgeBased:
            # Lakukan pencarian menggunakan cosine similarity
            query_vector = vectorizer.transform([grogInput])
            similarities = cosine_similarity(query_vector, vectorized_knowledge).flatten()
            
            # Pilih hasil pencarian dengan similaritas tertinggi
            top_results = [st.session_state.knowledgeBased[i] for i in similarities.argsort()[-5:][::-1]]

            if top_results:
                combinedInput = "\n\n".join([result["content"] for result in top_results]) + "\n\n" + grogInput
            else:
                combinedInput = grogInput
        else:
            combinedInput = grogInput
        
        response = response.invoke({"text": combinedInput, "language": language})
        response = response.content

        # Tambahkan input dan response ke dalam Index dan knowledgeBased
        st.session_state.knowledgeBased.append({"input":grogInput,"content": response})
    except Exception as e:
        response = f"Maaf, permintaan anda tidak dapat dilakukan saat ini. Error: {e}"

    # Menampilkan response dari groq atau pencarian
    with st.chat_message("assistant"):
        st.markdown(response)
    # Menambahkan response groq ke dalam chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    # Menambahkan response ke memori
    st.session_state.memory.append({
        "role": "assistant",
        "content": response
    })
