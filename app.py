import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import langid
from lib import readPDF, rag, textChunk, slidingWindowContext

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

# Inisialisasi Knowledge based, messages history, memory dan file status
if "knowledgeBased" not in st.session_state:
    st.session_state.knowledgeBased = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory" not in st.session_state:
    st.session_state.memory = []
if "fileUploaded" not in st.session_state:
    st.session_state.fileUploaded = False

# Upload PDF
file = st.file_uploader("Upload PDF", type="pdf")
if file:
    fileContents = readPDF(file)
    st.success("File berhasil di-upload!")
else:
    st.session_state.fileUploaded = False 
    
# Tampilkan histori chat ketika ada prompt baru
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if grogInput := st.chat_input("Apa yang ingin Anda ketahui?"):

    # Deteksi bahasa input menggunakan langid
    language, confidence = langid.classify(grogInput)

    # Fungsi merangkum teks
    def sumText(text):
        prompt = groqPrompt | chat
        response = prompt.invoke({"text": text, "language": language}).content

        return response

    try:
        # Cek apakah file baru di-upload, jika ya tambahkan ke knowledgeBased
        if file and not st.session_state.fileUploaded:
            # Lakukan chunking pada konten file PDF
            fileChunks = list(textChunk(fileContents))

            # Tambahkan semua chunk ke dalam knowledgeBased
            for chunk in fileChunks:
                # membuat summary dari chunk text yang diberikan
                summary = sumText(chunk)
                st.session_state.knowledgeBased.append({"input": "Summary", "content": summary})

            st.session_state.fileUploaded = True 

        # Tampilkan pesan dari user
        st.chat_message("user").markdown(grogInput)
        
        st.session_state.messages.append({"role": "user", "content": grogInput})
        st.session_state.memory.append({"role": "user", "content": grogInput})

        # Lakukan chunking pada input user yang lebih dari 4000 tokens
        inputChunk = list(textChunk(grogInput)) if len(grogInput.split()) > 3000 else [grogInput]

        combineResponse = []
        for chunk in inputChunk:
            tempResponse = groqPrompt | chat
            response = tempResponse.invoke({"text": chunk, "language": language}).content
            combineResponse.append(response)

        response = ' '.join(combineResponse)

        combinedInput = rag(grogInput, st.session_state.knowledgeBased)

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
