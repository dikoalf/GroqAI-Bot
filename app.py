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
Selalu menjawab pertanyaan menggunakan bahasa {language}.
"""
human = "{text}"
groqPrompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

# Inisialisasi Index, TfidfVectorizer, dan Memory
index = minsearch.Index(text_fields=["input", "content"], keyword_fields=[])
vectorizer = TfidfVectorizer()

if "knowledgeBased" not in st.session_state:
    st.session_state.knowledgeBased = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory" not in st.session_state:
    st.session_state.memory = []
if "fileUploaded" not in st.session_state:
    st.session_state.fileUploaded = False

# Fungsi membaca PDF
def readPDF(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Fungsi vectorize texts
def vectorizeText(texts):
    return vectorizer.fit_transform(texts)

# Fungsi memecah teks jadi chunks
def textChunk(text, chunk_size=4000):
    tokens = text.split()
    for i in range(0, len(tokens), chunk_size):
        yield ' '.join(tokens[i:i + chunk_size])

# Fungsi sliding window untuk memori percakapan
def slidingWindowContext(messages, window_size=5):
    return messages[-window_size:]

# Upload PDF
file = st.file_uploader("Upload PDF", type="pdf")
if file:
    fileContents = readPDF(file)

# Menampilkan histori chat ketika ada prompt baru
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if grogInput := st.chat_input("Apa yang ingin Anda ketahui?"):

    try:
        # Deteksi bahasa input menggunakan langid
        language, confidence = langid.classify(grogInput)

        if file and not st.session_state.fileUploaded:
            # Lakukan chunking pada konten file PDF
            fileChunks = list(textChunk(fileContents))
            
            # Tambahkan semua chunk ke dalam knowledgeBased
            for chunk in fileChunks:
                st.session_state.knowledgeBased.append({"input": "File", "content": chunk})

            st.session_state.fileUploaded = True
        else:
            st.warning("Anda sudah meng-upload file PDF. Hanya satu file yang diizinkan.")


        # Tampilkan pesan dari user
        st.chat_message("user").markdown(grogInput)
        st.session_state.messages.append({"role": "user", "content": grogInput})
        st.session_state.memory.append({"role": "user", "content": grogInput})

        # Lakukan chunking pada input user yang lebih dari 4000 tokens
        inputChunk = list(textChunk(grogInput)) if len(grogInput.split()) > 4000 else [grogInput]

        combineResponse = []
        for chunk in inputChunk:
            tempResponse = groqPrompt | chat
            response = tempResponse.invoke({"text": chunk, "language": language}).content
            combineResponse.append(response)

        response = ' '.join(combineResponse)

        # Tambahkan percakapan ke knowledgeBase dan lakukan pencarian similarity
        if st.session_state.knowledgeBased:
            knowledgeText = [item["content"] for item in st.session_state.knowledgeBased]
            vectorizedKnowledge = vectorizeText(knowledgeText)
            query = vectorizer.transform([grogInput])
            similarities = cosine_similarity(query, vectorizedKnowledge).flatten()

            # Pilih hasil pencarian dengan similarity tertinggi
            topResults = [st.session_state.knowledgeBased[i] for i in similarities.argsort()[-5:][::-1]]

            if topResults:
                combinedInput = "\n\n".join([result["content"] for result in topResults]) + "\n\n" + grogInput
            else:
                combinedInput = grogInput
        else:
            combinedInput = grogInput

        # Ambil window percakapan terakhir menggunakan sliding window
        relevantContext = slidingWindowContext(st.session_state.memory)

        # Gabungkan konteks window terakhir dengan input baru
        memoryContext = "\n\n".join([item["content"] for item in relevantContext])
        finalInput = memoryContext + "\n\n" + combinedInput

        # Menghasilkan respons final
        finalResponse = groqPrompt | chat
        finalResponse = finalResponse.invoke({"text": finalInput, "language": language}).content

        # Tambahkan input dan response ke knowledgeBase dan memori
        st.session_state.knowledgeBased.append({"input": grogInput, "content": finalResponse})
    except Exception as e:
        finalResponse = f"Maaf, permintaan anda tidak dapat dilakukan saat ini. Error: {e}"
    
    # Tampilkan respons
    with st.chat_message("assistant"):
        st.markdown(finalResponse)
    
    st.session_state.messages.append({"role": "assistant", "content": finalResponse})
    st.session_state.memory.append({"role": "assistant", "content": finalResponse})