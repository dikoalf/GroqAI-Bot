import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import langid
from lib import readPDF, rag, textChunk, slidingWindowContext

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
system = """Kamu adalah asisten. Jawablah dalam bahasa {language} sesuai dengan preferensi pengguna."""
human = "{text}"
groqPrompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

# Inisialisasi Knowledge based, messages history
if "knowledgeBased" not in st.session_state:
    st.session_state.knowledgeBased = []
if "messages" not in st.session_state:
    st.session_state.messages = []

def processFile():
    if st.session_state["fileUploader"]:
        fileContents = readPDF(st.session_state["fileUploader"])
        fileName = st.session_state["fileUploader"].name.lower()

        # Lakukan chunking pada konten file PDF
        fileChunks = list(textChunk(fileContents))
        # Tambahkan semua chunk ke dalam knowledgeBased
        for idx, chunk in enumerate(fileChunks):
            st.session_state.knowledgeBased.append({"input": f"File:{fileName}  - Part {idx+1}", "content": chunk})
            
# Upload PDF
file = st.file_uploader("Upload PDF", type="pdf", key="fileUploader", on_change=processFile)

if file:
    st.success("File berhasil di-upload!")

# Tampilkan histori chat ketika ada prompt baru
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
        
        # Lakukan chunking pada input user yang lebih dari 3000 tokens
        inputChunk = list(textChunk(grogInput, 3000)) if len(grogInput.split()) > 3000 else [grogInput]
        combineResponse = []
        for chunk in inputChunk:
            tempResponse = groqPrompt | chat
            response = tempResponse.invoke({"text": chunk, "language": language}).content
            combineResponse.append(response)
        response = ' '.join(combineResponse)
        
        combinedInput = rag(grogInput, knowledgeBase)

        # Mengambil percakapan terakhir menggunakan sliding window
        relevantContext = slidingWindowContext(messageHistory)
        
        # Menggabungkan konteks window terakhir dengan input baru
        memoryContext = "\n\n".join([item["content"] for item in relevantContext])
        finalInput = memoryContext + "\n\n" + combinedInput
        
        # Menghasilkan respons final
        finalResponse = groqPrompt | chat
        finalResponse = finalResponse.invoke({"text": finalInput, "language": language}).content
        
        # Menambahkan input dan response ke knowledgeBase
        knowledgeBase.append({"input": grogInput, "content": finalResponse})
    except Exception as e:
        finalResponse = f"Maaf, permintaan anda tidak dapat dilakukan saat ini."
        
    # Tampilkan respons
    with st.chat_message("assistant"):
        st.markdown(finalResponse)
        
    messageHistory.append({"role": "assistant", "content": finalResponse})
