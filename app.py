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
system = """Kamu adalah asisten. 
Jawablah dalam bahasa {language} sesuai dengan preferensi pengguna.
"""
human = "{text}"
groqPrompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

# Inisialisasi LLM untuk melakukan summary
sumKey = os.getenv("GROQ_AI_API_KEY2")
chatSum = ChatGroq(
    temperature=0,
    model="gemma2-9b-it",
    api_key=sumKey
)

# Membuat template percakapan
systemSum = """
Kamu adalah asisten yang bertugas untuk membuat ringkasan dari teks yang diberikan.
Berikan ringkasan yang singkat, padat, dan jelas dari teks, dengan menjaga informasi penting tetap utuh.
Jawablah dalam bahasa {language} sesuai dengan preferensi pengguna.
Jika teksnya terlalu panjang, fokuslah pada poin-poin kunci dan pastikan tidak ada detail penting yang terlewat.
"""
sumPrompt = ChatPromptTemplate.from_messages([("system", systemSum), ("human", human)])

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

# Fungsi merangkum teks
def sumText(text, lang):
    prompt = sumPrompt | chatSum
    response = prompt.invoke({"text": text, "language": lang}).content

    return response


# React to user input
if grogInput := st.chat_input("Apa yang ingin Anda ketahui?"):
    
    # Deteksi bahasa input menggunakan langid
    language, confidence = langid.classify(grogInput)

    try:
        knowledgeBase = st.session_state.knowledgeBased
        memory = st.session_state.memory
        chatHistory = st.session_state.messages

        # Tampilkan pesan dari user
        st.chat_message("user").markdown(grogInput)
        chatHistory.append({"role": "user", "content": grogInput})
        memory.append({"role": "user", "content": grogInput})

        # Cek apakah file baru di-upload, jika ya tambahkan ke knowledgeBased
        if file and not st.session_state.fileUploaded:
            # Lakukan chunking pada konten file PDF
            fileChunks = list(textChunk(fileContents))

            # Tambahkan semua chunk ke dalam knowledgeBased
            for chunk in fileChunks:
                st.session_state.knowledgeBased.append({"input": "File", "content": chunk})

                summary = sumText(chunk, language)
                knowledgeBase.append({"input": "Summary", "content": summary})

            st.session_state.fileUploaded = True 

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
        relevantContext = slidingWindowContext(memory)

        # Menggabungkan konteks window terakhir dengan input baru
        memoryContext = "\n\n".join([item["content"] for item in relevantContext])
        finalInput = memoryContext + "\n\n" + combinedInput

        # Menghasilkan respons final
        finalResponse = groqPrompt | chat
        finalResponse = finalResponse.invoke({"text": finalInput, "language": language}).content

        # Menambahkan input dan response ke knowledgeBase
        knowledgeBase.append({"input": grogInput, "content": finalResponse})
    except Exception as e:
        finalResponse = f"Maaf, permintaan anda tidak dapat dilakukan saat ini. Error: {e}"
    
    # Tampilkan respons
    with st.chat_message("assistant"):
        st.markdown(finalResponse)
    
    chatHistory.append({"role": "assistant", "content": finalResponse})
    memory.append({"role": "assistant", "content": finalResponse})
