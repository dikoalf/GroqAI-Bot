import os
import datetime
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import langid
from lib import readPDF, rag, textChunk, slidingWindowContext, saveToDrive, googleAuth

st.title("Groq Bot")
load_dotenv()

# Inisialisasi GroqAI
# Inisialisasi LLM untuk chat
key = os.getenv("GROQ_AI_API_KEY")
chat = ChatGroq(
    temperature=0,
    model="llama3-70b-8192",
    api_key=key
)

# Membuat template percakapan
system = """Kamu adalah asisten yang ceria dan positif.
Selalu menjawab dalam bahasa {language}, sesuai dengan preferensi pengguna. 
Jika tidak dapat mendeteksi bahasa, gunakan bahasa Indonesia sebagai default.
"""
human = "{text}"
groqPrompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

# Inisialisasi Google 
drive = googleAuth()
folderID = "input your folder id"

# Inisialisasi Knowledge based, messages history
if "knowledgeBased" not in st.session_state:
    st.session_state.knowledgeBased = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "errorLog" not in st.session_state:
    st.session_state.errorLog = []

def processFile():
    if st.session_state["fileUploader"]:
        fileContents = readPDF(st.session_state["fileUploader"])
        fileName = st.session_state["fileUploader"].name.lower()
        st.write(fileName)
        # Lakukan chunking pada konten file PDF
        fileChunks = list(textChunk(fileContents))
        # Tambahkan semua chunk ke dalam knowledgeBased
        for idx, chunk in enumerate(fileChunks):
            st.session_state.knowledgeBased.append({"input": f"File:{fileName} - Part {idx+1}", "content": chunk})

# Upload PDF
file = st.file_uploader("Upload PDF", type="pdf", key="fileUploader", on_change=processFile)

if file:
    st.success("File berhasil di-upload!")

# Fungsi untuk memisahkan teks dan kode
def displayMessage(message):
    parts = message.split('```')
    for i, part in enumerate(parts):
        if i % 2 == 0:
            st.markdown(part)
        else:
            st.code(part)

# Tampilkan histori chat ketika ada prompt baru
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        displayMessage(message["content"])

# React to user input
if grogInput := st.chat_input("Apa yang ingin Anda ketahui?"):
    # Deteksi bahasa input menggunakan langid
    language, confidence = langid.classify(grogInput)
    try:
        knowledgeBase = st.session_state.knowledgeBased
        messageHistory = st.session_state.messages
        
        # Tampilkan pesan dari user
        st.chat_message("user").markdown(grogInput)
        messageHistory.append({"role": "user", "content": grogInput})
        
        # Lakukan chunking pada input user yang lebih dari 2500 tokens
        inputChunk = list(textChunk(grogInput, 2500)) if len(grogInput.split()) > 2500 else [grogInput]
        combineResponse = []
        for chunk in inputChunk:
            tempResponse = groqPrompt | chat
            response = tempResponse.invoke({"text": chunk, "language": language}).content
            combineResponse.append(response)
        response = ' '.join(combineResponse)
        
        combinedInput = rag(grogInput, knowledgeBase)
        
        # Menghasilkan respons final
        finalResponse = groqPrompt | chat
        finalResponse = finalResponse.invoke({"text": combinedInput, "language": language}).content
        
        # Menambahkan input dan response ke knowledgeBase
        knowledgeBase.append({"input": grogInput, "content": finalResponse})
    except Exception as e:
        errorLogEntry = f"{datetime.datetime.now()}: {str(e)}"
        st.session_state.errorLog.append(errorLogEntry)
        saveToDrive(st.session_state.errorLog, drive, "errorLog.json", folderID)
        finalResponse = f"Maaf, permintaan Anda tidak dapat dilakukan saat ini."
        
    # Tampilkan respons
    with st.chat_message("assistant"):
        displayMessage(finalResponse)
        
    messageHistory.append({"role": "assistant", "content": finalResponse})

    saveToDrive(messageHistory, drive, "memory.json", folderID)
