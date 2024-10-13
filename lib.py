import fitz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer()

# Fungsi membaca PDF
def readPDF(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# fungsi melakukan retrieval augmented generation
def rag(text,data):
    # Tambahkan percakapan ke knowledgeBase dan lakukan pencarian similarity
    if data:
        knowledgeText = [item["content"] for item in data]
        vectorizedKnowledge = vectorizer.fit_transform(knowledgeText)
        query = vectorizer.transform([text])
        similarities = cosine_similarity(query, vectorizedKnowledge).flatten()

        # Pilih hasil pencarian dengan similarity tertinggi
        topResults = [data[i] for i in similarities.argsort()[-5:][::-1]]

        if topResults:
            combinedInput = "\n\n".join([result["content"] for result in topResults]) + "\n\n" + text
        else:
            combinedInput = text
    else:
        combinedInput = text
    
    return combinedInput

# Fungsi memecah teks jadi chunks
def textChunk(text, size=500):
    tokens = text.split()
    for i in range(0, len(tokens), size):
        chunk = ' '.join(tokens[i:i + size])
        yield chunk

# Fungsi sliding window untuk memori percakapan
def slidingWindowContext(messages, window_size=5):
    return messages[-window_size:]