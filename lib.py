import fitz
import minsearch

# Fungsi membaca PDF
def readPDF(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# fungsi melakukan retrieval augmented generation
def rag(text,data):
    # Initialize MinSearch Index
    index = minsearch.Index(text_fields=["input","content"], keyword_fields=[])

    # Tambahkan percakapan ke knowledgeBase dan lakukan pencarian similarity
    if data:
        # memperbarui index dengan data dari session knowledgebase
        index.fit(data)
        
        # melakukan search bedasarkan query
        searchResult = index.search(
            query=text, 
            boost_dict={'content': 3.0, 'input': 0.5},
            num_results=1
        )

        if searchResult:
            combinedInput = "\n\n".join([result["content"] for result in searchResult]) + "\n\n" + text
        else:
            combinedInput = text
    else:
        combinedInput = text

    return combinedInput

# Fungsi memecah teks jadi chunks
def textChunk(text, size=3000):
    tokens = text.split()
    for i in range(0, len(tokens), size):
        chunk = ' '.join(tokens[i:i + size])
        yield chunk

# Fungsi sliding window untuk memori percakapan
def slidingWindowContext(messages, window_size=5):
    return messages[-window_size:]