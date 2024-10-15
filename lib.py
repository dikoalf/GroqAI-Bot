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
    # Inisialisasi index
    index = minsearch.Index(text_fields=["content","input"], keyword_fields=[])

    # memasukan data ke index
    if data:
        index.fit(data)

        # melakukan search bedasarkan input text
        searchResult = index.search(
            query=text, 
            boost_dict={'content': 5.0, 'input': 1},
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
def textChunk(text, size=500):
    tokens = text.split()
    for i in range(0, len(tokens), size):
        chunk = ' '.join(tokens[i:i + size])
        yield chunk

# Fungsi sliding window untuk memori percakapan
def slidingWindowContext(messages, window_size=5):
    return messages[-window_size:]